from flask import request,Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from numpy import identity
from models import db, Patient, Department, Appointment, Doctor, DoctorAvailability
from cache import get_cache, set_cache,delete_cache
from utils import success, error,  serialize_patient, serialize_appointment, serialize_doctor, serialize_availability

pat_bp=Blueprint('patient', __name__)

@pat_bp.route('/api/patient/dashboard', methods=['GET'])
@jwt_required()
def patient_dashboard():
    identity=get_jwt_identity()
    role, patient_id = identity.split(":")
    if role != "patient":
        return error("Unauthorized", 403)
    patient_id=int(patient_id)
    patient     = Patient.query.get_or_404(patient_id)
    departments = Department.query.all()

    appointments = Appointment.query.filter(
        Appointment.patient_id == patient.patient_id,
        Appointment.status.in_(["BOOKED"])
    ).order_by(Appointment.date.asc(), Appointment.time.asc()).all()

    appointments_data = []
    for appt in appointments:
        queue = Appointment.query.filter_by(
            doctor_id=appt.doctor_id,
            date=appt.date,
            time=appt.time,
            status='BOOKED'
        ).order_by(Appointment.app_id.asc()).all()

        appt_dict = serialize_appointment(appt)
        appt_dict['token_no'] = next(
            (i + 1 for i, a in enumerate(queue) if a.app_id == appt.app_id), None
        )
        appointments_data.append(appt_dict)

    return success({
        "patient":      serialize_patient(patient),
        "departments":  [{"dep_id": d.dep_id, "dep_name": d.dep_name, "dep_des": d.dep_des} for d in departments],
        "appointments": appointments_data,
    })

@pat_bp.route('/api/patient/history', methods=['GET'])
@jwt_required()
def patient_history():
    identity = get_jwt_identity()
    
    role, pid_str = identity.split(":")
    if role != 'patient':
        return error("Patient authentication required", 403)
    patient_id = int(pid_str)
    
    patient      = Patient.query.get_or_404(patient_id)
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(
        Appointment.date.desc()
    ).all()

    return success({
        "patient":      serialize_patient(patient),
        "appointments": [serialize_appointment(a, include_treatment=True) for a in appointments],
    })

@pat_bp.route('/api/patient/profile', methods=['PUT'])
@jwt_required()
def edit_patient():
    identity = get_jwt_identity()
    
    role, pid_str = identity.split(":")
    if role != 'patient':
        return error("Patient authentication required", 403)
    patient_id = int(pid_str)

    patient = Patient.query.get_or_404(patient_id)
    body    = request.get_json(force=True)

    new_username = body.get('patient_username', patient.patient_username)
    new_email    = body.get('email', patient.email)

    if new_username != patient.patient_username:
        if Patient.query.filter_by(patient_username=new_username).first():
            return error("Username already taken")

    if new_email != patient.email:
        if Patient.query.filter_by(email=new_email).first():
            return error("Email already in use")

    patient.patient_name     = body.get('patient_name', patient.patient_name)
    patient.patient_username = new_username
    patient.email            = new_email
    patient.phone            = body.get('phone',patient.phone)
    patient.gender           = body.get('gender', patient.gender)
    patient.age              = body.get('age',patient.age)
    patient.address          = body.get('address',patient.address)

    db.session.commit()
    return success(serialize_patient(patient), "Profile updated successfully")

@pat_bp.route('/api/patient/departments/<int:dep_id>', methods=['GET'])
@jwt_required()
def patient_department_details(dep_id):
    identity = get_jwt_identity()
    
    role, pid_str = identity.split(":")
    if role != 'patient':
        return error("Patient authentication required", 403)
    

    department = Department.query.get_or_404(dep_id)
    doctors    = Doctor.query.filter_by(dep_id=dep_id).all()

    return success({
        "department": {
            "dep_id":   department.dep_id,
            "dep_name": department.dep_name,
            "dep_des":  department.dep_des,
        },
        "doctors": [serialize_doctor(d) for d in doctors],
    })


@pat_bp.route('/api/patient/doctors/<int:doctor_id>', methods=['GET'])
@jwt_required()
def patient_doctor_details(doctor_id):
    identity = get_jwt_identity()
    
    role, pid_str = identity.split(":")
    if role != 'patient':
        return error("Patient authentication required", 403)

    cache_key = f"doctor:availability:{doctor_id}"
    cached    = get_cache(cache_key)

    if cached:
        doctor_data  = cached["doctor"]
        availability = cached["availability"]
    else:
        doctor = Doctor.query.get_or_404(doctor_id)
        today  = datetime.today().date()

        availability_rows = DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.date >= today
        ).order_by(
            DoctorAvailability.date.asc(),
            DoctorAvailability.start_time.asc()
        ).all()

        doctor_data  = serialize_doctor(doctor)
        availability = [serialize_availability(av) for av in availability_rows]

        set_cache(cache_key, {"doctor": doctor_data, "availability": availability})

    slot_bookings = {}
    for av in availability:
        count = Appointment.query.filter_by(
            doctor_id=doctor_id,
            date=datetime.strptime(av["date"], "%Y-%m-%d").date(),
            time=datetime.strptime(av["start_time"], "%H:%M").time(),
            status='BOOKED'
        ).count()
        slot_bookings[av["availability_id"]] = count

    return success({
        "doctor":        doctor_data,
        "availability":  availability,
        "slot_bookings": slot_bookings,
        "slot_capacity": 10,
    })

@pat_bp.route('/api/patient/book/<int:availability_id>', methods=['POST'])
@jwt_required()
def book_appointment(availability_id):
    identity = get_jwt_identity()

    role, pid_str = identity.split(":")
    if role != 'patient':
        return error("Patient authentication required", 403)
    patient_id = int(pid_str)

    avail = DoctorAvailability.query.get_or_404(availability_id)

    if avail.date < datetime.today().date():
        return error("Cannot book past slots")

    existing_count = Appointment.query.filter_by(
        doctor_id=avail.doctor_id,
        date=avail.date,
        time=avail.start_time,
        status='BOOKED'
    ).count()

    if existing_count >= 10:
        return error("This slot is fully booked (10/10). Please choose another.")

    existing = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        Appointment.date       == avail.date,
        Appointment.time       == avail.start_time,
        Appointment.status.in_(['BOOKED', 'COMPLETED'])
    ).first()

    if existing:
        if existing.status == 'BOOKED':
            return error("You already have an appointment at this slot.", 409)
        else:
            return error("You have already completed an appointment at this slot.", 409)

    appt = Appointment(
        patient_id=patient_id,
        doctor_id=avail.doctor_id,
        status='BOOKED',
        date=avail.date,
        time=avail.start_time,
        visit_type=avail.slot_name,
    )
    db.session.add(appt)
    db.session.commit()
    return success(serialize_appointment(appt), "Appointment booked successfully", 201)


@pat_bp.route('/api/patient/appointments/<int:appointment_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_appointment(appointment_id):
    identity = get_jwt_identity()
    
    role, pid_str = identity.split(":")
    if role != 'patient':
        return error("Patient authentication required", 403)
    patient_id = int(pid_str)
    

    appt = Appointment.query.get_or_404(appointment_id)

    if appt.patient_id != patient_id:
        return error("Unauthorized", 403)

    if appt.status in ['COMPLETED', 'CANCELLED']:
        return error("This appointment cannot be cancelled.")

    appt.status = 'CANCELLED'
    db.session.commit()
    return success(serialize_appointment(appt), "Appointment cancelled successfully")

@pat_bp.route('/api/patient/export/csv', methods=['POST'])
@jwt_required()
def export_csv():
    identity = get_jwt_identity()

    role, pid_str = identity.split(":")
    if role != 'patient':
        return error("Patient authentication required", 403)
    patient_id = int(pid_str)

    patient = Patient.query.get_or_404(patient_id)
    
    if not patient.email:
        return error("No email address on file, cannot send the export")
 
    from celery_app import celery
    
    task = celery.send_task('tasks.export_patient_csv', args=[patient_id])
 
    return success(
        {"task_id": task.id},
        f"Export started — you will receive an email at {patient.email} shortly"
    )