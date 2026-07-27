import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date, timedelta
from celery import shared_task   # shared_task doesn't need to import celery_app - no circular import
from flask import Flask
from models import db, Appointment, Patient, Doctor, Treatment
import os
import io
from email.mime.base import MIMEBase
from email import encoders

GMAIL_SENDER       = "uglysimp44@gmail.com"     
GMAIL_APP_PASSWORD = "psre aros lkpq ynuz"      
GMAIL_SENDER_NAME  = "City Hospital"           

def create_app():
    app = Flask(__name__)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'sqlite:///' + os.path.join(BASE_DIR, 'hospital.db')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def send_email(to_address: str, subject: str, html_body: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{GMAIL_SENDER_NAME} <{GMAIL_SENDER}>"
    msg["To"]      = to_address
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()             
            server.starttls()        
            server.ehlo()           
            server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_SENDER, to_address, msg.as_string())

        print(f"[Email] Sent to {to_address}")

    except smtplib.SMTPAuthenticationError:
        print(f"[Email] Authentication failed; check GMAIL_SENDER and GMAIL_APP_PASSWORD")

    except smtplib.SMTPException as e:
        print(f"[Email]; Failed to send to {to_address}: {e}")

    except Exception as e:
        print(f"[Email]; Unexpected error for {to_address}: {e}")

def build_email_body(patient_name: str, doctor_name: str,
                     appointment_date: str, appointment_time: str) -> str:
    
    return f"""
    <html>
    <body>
        <h2>Hospital Appointment Reminder</h2>
        <p>Dear <strong>{patient_name}</strong>,</p>
        <p>This is a friendly reminder that you have an appointment scheduled at <strong>City Hospital</strong>:</p>
        
        <ul>
            <li><strong>Date:</strong> {appointment_date}</li>
            <li><strong>Time:</strong> {appointment_time}</li>
            <li><strong>Doctor:</strong> Dr. {doctor_name}</li>
        </ul>

        <p>Please arrive <strong>10 minutes early</strong> and bring any previous reports or prescriptions if applicable.</p>
        <p><small>System-generated reminder from City Hospital. Please do not reply to this email.</small></p>
    </body>
    </html>
    """

@shared_task(name="tasks.send_daily_reminders")
def send_daily_reminders():
    app = create_app()

    with app.app_context():
        today = date.today()
        appointments = Appointment.query.filter_by(
            date=today,
            status='BOOKED'
        ).all()

        if not appointments:
            print(f"[Reminders] No appointments for {today}. Nothing to send.")
            return {"sent": 0, "skipped": 0, "date": str(today)}

        print(f"[Reminders] Found {len(appointments)} appointment(s) for {today}.")

        sent_count    = 0
        skipped_count = 0

        for appt in appointments:
            patient = appt.patient
            doctor  = appt.doctor

            appointment_date = appt.date.strftime("%A, %d %B %Y")   
            appointment_time = appt.time.strftime("%I:%M %p")      

            subject   = f"Reminder: Your appointment on {appointment_date}"
            html_body = build_email_body(
                patient_name=patient.patient_name,
                doctor_name=doctor.doctor_name,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
            )

            send_email(
                to_address=patient.email,
                subject=subject,
                html_body=html_body,
            )
            sent_count += 1

        print(f"[Reminders] Done. Sent: {sent_count}, Skipped: {skipped_count}.")
        return {"sent": sent_count, "skipped": skipped_count, "date": str(today)}
    
@shared_task(name="tasks.send_monthly_report")
def send_monthly_report():
    app = create_app()
 
    with app.app_context():
        today                = date.today()
        first_day_this_month = today.replace(day=1)
        last_day_prev_month  = first_day_this_month - timedelta(days=1)
        first_day_prev_month = last_day_prev_month.replace(day=1)
        month_label          = first_day_prev_month.strftime("%B %Y")  
 
        print(f"[Monthly Report] Generating reports for {month_label}...")
        
        appointments = Appointment.query.filter(
            Appointment.status.in_(["COMPLETED", "CANCELLED"]),
            Appointment.date >= first_day_prev_month,
            Appointment.date <= last_day_prev_month,
        ).order_by(Appointment.date.asc()).all()
 
        if not appointments:
            print(f"[Monthly Report] No appointments found for {month_label}.")
            return {"sent": 0, "month": month_label}
 
        print(f"[Monthly Report] Found {len(appointments)} appointment(s). Grouping by doctor...")
 
        appt_dict = {}
 
        for appt in appointments:
            patient   = appt.patient
            doctor    = appt.doctor
            treatment = appt.treatment   
            
            if not doctor:
                print(f"[Monthly Report] Skipping appointment {appt.app_id} - doctor not found")
                continue
            if not patient:
                print(f"[Monthly Report] Skipping appointment {appt.app_id} - patient not found")
                continue
 
            if doctor.doctor_id not in appt_dict:
                appt_dict[doctor.doctor_id] = {
                    "doctor":       doctor,
                    "appointments": [],
                }
 
            appt_dict[doctor.doctor_id]["appointments"].append({
                "app_id":       appt.app_id,
                "patient_name": patient.patient_name,
                "date":         appt.date.strftime("%d %b %Y"),         
                "time":         appt.time.strftime("%I:%M %p"),         
                "status":       appt.status,
                "diagnosis":    treatment.diagnosis    if treatment else "N/A",
                "prescription": treatment.prescription if treatment else "N/A",
                "medication":   treatment.medication   if treatment else "N/A",
                "tests_done":   treatment.tests_done   if treatment else "N/A",
                "next_visit":   treatment.next_visit_date.strftime("%d %b %Y")
                                if treatment and treatment.next_visit_date else "N/A",
            })
 
        sent_count    = 0
        skipped_count = 0
 
        for doctor_id, data in appt_dict.items():
            doctor = data["doctor"]
            appts  = data["appointments"]
 
            if not doctor.doctor_email:
                print(f"[Monthly Report] Skipping Dr. {doctor.doctor_name} - no email on file")
                skipped_count += 1
                continue
 
            total_appts = len(appts)
            completed   = sum(1 for a in appts if a["status"] == "COMPLETED")
            cancelled   = sum(1 for a in appts if a["status"] == "CANCELLED")
 
            rows_html = ""
            for a in appts:
                rows_html += f"""
                <tr>
                    <td>{a['app_id']}</td>
                    <td>{a['patient_name']}</td>
                    <td>{a['date']}</td>
                    <td>{a['time']}</td>
                    <td>{a['status']}</td>
                    <td>{a['diagnosis']}</td>
                    <td>{a['prescription']}</td>
                    <td>{a['medication']}</td>
                    <td>{a['tests_done']}</td>
                    <td>{a['next_visit']}</td>
                </tr>
                """
 
            html_body = f"""
            <html>
            <body>
                <h2>Monthly Activity Report</h2>
                <p>Dear <strong>Dr. {doctor.doctor_name}</strong>,</p>
                <p>Here is your activity summary for <strong>{month_label}</strong>. This report covers all completed and cancelled appointments along with the treatments provided.</p>
 
                <h3>Summary</h3>
                <ul>
                    <li><strong>Total Appointments:</strong> {total_appts}</li>
                    <li><strong>Completed:</strong> {completed}</li>
                    <li><strong>Cancelled:</strong> {cancelled}</li>
                </ul>
 
                <h3>Appointment Details</h3>
                <table border="1" cellpadding="8" cellspacing="0" style="text-align: left; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Patient</th>
                            <th>Date</th>
                            <th>Time</th>
                            <th>Status</th>
                            <th>Diagnosis</th>
                            <th>Prescription</th>
                            <th>Medication</th>
                            <th>Tests Done</th>
                            <th>Next Visit</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
 
                <p><small>System-generated monthly activity report for City Hospital. Generated on {today.strftime("%d %B %Y")}.</small></p>
            </body>
            </html>
            """
 
            send_email(
                to_address=doctor.doctor_email,
                subject=f"Monthly Activity Report - {month_label}",
                html_body=html_body,
            )
            sent_count += 1
            print(f"[Monthly Report] Sent to Dr. {doctor.doctor_name} ({doctor.doctor_email})")
 
        print(f"[Monthly Report] Done. Sent: {sent_count}, Skipped: {skipped_count}.")
        return {"sent": sent_count, "skipped": skipped_count, "month": month_label}
        
def send_email_with_attachment(to_address: str, subject: str,body_text: str, csv_content: str,filename: str):
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"]    = f"{GMAIL_SENDER_NAME} <{GMAIL_SENDER}>"
    msg["To"]      = to_address

    msg.attach(MIMEText(body_text, "plain"))
 
    attachment = MIMEBase("application", "octet-stream")
    attachment.set_payload(csv_content.encode("utf-8"))
    encoders.encode_base64(attachment)   
    attachment.add_header(
        "Content-Disposition",
        "attachment",
        filename=filename   
    )
    msg.attach(attachment)
 
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_SENDER, to_address, msg.as_string())
        print(f"[CSV Export] Sent to {to_address}")
 
    except smtplib.SMTPAuthenticationError:
        print(f"[CSV Export] Authentication failed")
 
    except smtplib.SMTPException as e:
        print(f"[CSV Export] Failed to send to {to_address}: {e}")
 
    except Exception as e:
        print(f"[CSV Export] Unexpected error: {e}")
 
            
@shared_task(name="tasks.export_patient_csv")
def export_patient_csv(patient_id):
    app = create_app()
 
    with app.app_context():
        patient = Patient.query.get(patient_id)
 
        if not patient:
            print(f"[CSV Export] Patient {patient_id} not found aborting")
            return {"success": False, "reason": "patient not found"}
 
        if not patient.email:
            print(f"[CSV Export] Patient {patient_id} has no email aborting")
            return {"success": False, "reason": "no email on file"}
 
        print(f"[CSV Export] Generating CSV for {patient.patient_name} (id={patient_id})...")
 
        appointments = Appointment.query.filter_by(
            patient_id=patient_id
        ).order_by(Appointment.date.asc()).all()
 
        if not appointments:
            print(f"[CSV Export] No appointments found for patient {patient_id}")
            
        output = io.StringIO()
        writer = csv.writer(output)
 
        writer.writerow([
            "Appointment ID",
            "Date",
            "Time",
            "Doctor",
            "Department",
            "Status",
            "Diagnosis",
            "Prescription",
            "Medication",
            "Tests Done",
            "Next Visit Date",
        ])
 
        for appt in appointments:
            doctor    = appt.doctor
            treatment = appt.treatment
 
            writer.writerow([
                appt.app_id,
                appt.date.strftime("%d %b %Y"),
                appt.time.strftime("%I:%M %p"),
                f"Dr. {doctor.doctor_name}" if doctor else "N/A",
                doctor.department.dep_name  if doctor and doctor.department else "N/A",
                appt.status,
                treatment.diagnosis      if treatment else "N/A",
                treatment.prescription   if treatment else "N/A",
                treatment.medication     if treatment else "N/A",
                treatment.tests_done     if treatment else "N/A",
                treatment.next_visit_date.strftime("%d %b %Y")
                    if treatment and treatment.next_visit_date else "N/A",
            ])
 
        csv_content = output.getvalue()
        output.close()
 
        total      = len(appointments)
        completed  = sum(1 for a in appointments if a.status == "COMPLETED")
        filename   = f"treatment_history_{patient.patient_username}_{date.today()}.csv"
 
        body_text = (
            f"Dear {patient.patient_name},\n\n"
            f"Your treatment history export is ready. Please find it attached.\n\n"
            f"Summary:\n"
            f"  Total appointments : {total}\n"
            f"  Completed          : {completed}\n"
            f"  Other              : {total - completed}\n\n"
            f"This is an automated export from City Hospital.\n"
            f"Please do not reply to this email.\n"
        )
 
        send_email_with_attachment(
            to_address=patient.email,
            subject="Your Treatment History Export - City Hospital",
            body_text=body_text,
            csv_content=csv_content,
            filename=filename,
        )
 
        print(f"[CSV Export] Done for {patient.patient_name}.")
        return {
            "success":    True,
            "patient_id": patient_id,
            "rows":       total,
            "filename":   filename,
        }