from flask import request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta, time as dtime
from models import db, Doctor, Patient, Appointment, DoctorAvailability, Treatment
from cache import delete_cache, set_cache, get_cache
from utils import success, error, serialize_doctor, serialize_patient, serialize_appointment,serialize_treatment

doc_bp=Blueprint('doctor', __name__)
SLOTS={ "Morning": (dtime(9,0), dtime(12,0)),
        "Afternoon": (dtime(13,0), dtime(16,0)),
        "Evening": (dtime(17,0), dtime(20,0))
      }

@doc_bp.route('/api/doctor/dashboard',methods=["GET"])
@jwt_required()
def doctor_dashboard():
    identity=get_jwt_identity()
    role, doctor_id = identity.split(":")
    if role != "doctor":
        return error("Unauthorized", 403)
    doctor_id=int(doctor_id)
    doctor=Doctor.query.get(doctor_id)
    appointments = Appointment.query.filter(Appointment.doctor_id == doctor_id,Appointment.status.in_(["BOOKED"])).order_by(
        Appointment.date.asc(),
        Appointment.time.asc()
    ).all()
    all_patient_ids = db.session.query(Appointment.patient_id).filter_by(
        doctor_id=doctor_id
    ).distinct()

    assigned_patients = Patient.query.filter(
        Patient.patient_id.in_(all_patient_ids)
    ).all()

    return success({
        "doctor": serialize_doctor(doctor),
        "appointments": [serialize_appointment(a) for a in appointments],
        "assigned_patients": [serialize_patient(patient) for patient in assigned_patients]
    })

@doc_bp.route('/api/doctor/patients/<int:patient_id>', methods=['GET'])
@jwt_required()
def doctor_view_patient(patient_id):
    identity=get_jwt_identity()
    role, doctor_id = identity.split(":")
    if role != "doctor":
        return error("Unauthorized", 403)
    doctor_id=int(doctor_id)

    patient = Patient.query.get_or_404(patient_id)
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(
        Appointment.date.desc(), Appointment.time.desc()
    ).all()

    return success({
        "patient":      serialize_patient(patient),
        "appointments": [serialize_appointment(a, include_treatment=True) for a in appointments],
    })

@doc_bp.route('/api/doctor/appointments/<int:app_id>/complete', methods=['POST'])
@jwt_required()
def doctor_complete(app_id):
    identity=get_jwt_identity()
    role, doctor_id = identity.split(":")
    if role != "doctor":
        return error("Unauthorized", 403)
    doctor_id=int(doctor_id)

    appt = Appointment.query.get_or_404(app_id)

    if appt.doctor_id != doctor_id:
        return error("Unauthorized", 403)

    if appt.status != 'BOOKED':
        return error("Only BOOKED appointments can be marked as completed")

    appt.status = "COMPLETED"
    db.session.commit()
    return success(serialize_appointment(appt), "Appointment marked as completed")

@doc_bp.route('/api/doctor/appointments/<int:app_id>/cancel', methods=['POST'])
@jwt_required()
def doctor_cancel(app_id):
    identity=get_jwt_identity()
    role, doctor_id = identity.split(":")
    if role != "doctor":
        return error("Unauthorized", 403)
    doctor_id=int(doctor_id)
    appt = Appointment.query.get_or_404(app_id)

    if appt.doctor_id != doctor_id:
        return error("Unauthorized", 403)

    if appt.status in ('COMPLETED', 'CANCELLED'):
        return error("This appointment cannot be cancelled")

    appt.status = "CANCELLED"
    db.session.commit()
    return success(serialize_appointment(appt), "Appointment cancelled")

@doc_bp.route('/api/doctor/appointments/<int:app_id>/treatment', methods=['GET', 'POST'])
@jwt_required()
def appointment_treatment(app_id):
    identity=get_jwt_identity()
    role, doctor_id = identity.split(":")
    if role != "doctor":
        return error("Unauthorized", 403)
    doctor_id=int(doctor_id)

    appt = Appointment.query.get_or_404(app_id)

    if appt.doctor_id != doctor_id:
        return error("Unauthorized", 403)

    if request.method == 'GET':
        return success({
            "appointment": serialize_appointment(appt),
            "treatment":   serialize_treatment(appt.treatment),
        })

    body = request.get_json(force=True)

    if appt.treatment:
        t = appt.treatment
    else:
        t = Treatment(app_id=appt.app_id)
        db.session.add(t)

    t.diagnosis    = body.get('diagnosis')
    t.prescription = body.get('prescription')
    t.medication   = body.get('medication')
    t.tests_done   = body.get('tests_done')

    next_visit_raw = body.get('next_visit_date')
    if next_visit_raw:
        
        t.next_visit_date = datetime.strptime(next_visit_raw, "%Y-%m-%d").date()
    else:
        t.next_visit_date = None

    db.session.commit()
    return success(serialize_treatment(t), "Treatment saved successfully")


@doc_bp.route('/api/doctor/appointments/history', methods=['GET'])
@jwt_required()
def doctor_appointment_history():
    identity=get_jwt_identity()
    role, doctor_id = identity.split(":")
    if role != "doctor":
        return error("Unauthorized", 403)
    doctor_id=int(doctor_id)
    
    appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.status.in_(["COMPLETED", "CANCELLED"])
    ).order_by(Appointment.date.desc(), Appointment.time.desc()).all()

    return success({
        "appointments": [serialize_appointment(a, include_treatment=True) for a in appointments]
    })


@doc_bp.route('/api/doctor/patients/<int:patient_id>/blacklist', methods=['POST'])
@jwt_required()
def doctor_blacklist_patient(patient_id):
    identity = get_jwt_identity()
    role, doctor_id = identity.split(":")
    if role != "doctor":
        return error("Unauthorized", 403)
    doctor_id=int(doctor_id)
    patient = Patient.query.get_or_404(patient_id)
    patient.is_blacklisted = True
    db.session.commit()

    delete_cache("patients:list")
    return success(serialize_patient(patient), "Patient blacklisted successfully")


@doc_bp.route('/api/doctor/patients/<int:patient_id>/unblacklist', methods=['POST'])
@jwt_required()
def doctor_unblacklist_patient(patient_id):
    identity = get_jwt_identity()
    role, doctor_id = identity.split(":")
    if role != "doctor":
        return error("Unauthorized", 403)
    doctor_id=int(doctor_id)

    patient = Patient.query.get_or_404(patient_id)
    patient.is_blacklisted = False
    db.session.commit()

    delete_cache("patients:list")
    return success(serialize_patient(patient), "Patient unblacklisted successfully")

@doc_bp.route('/api/doctor/availability',methods=["GET","POST"])
@jwt_required()
def doctor_availability():
    identity=get_jwt_identity()
    role, doctor_id = identity.split(":")
    if role != "doctor":
        return error("Unauthorized", 403)
    doctor_id=int(doctor_id)

    today     = datetime.today().date()
    dates     = [today + timedelta(days=i) for i in range(7)]

    if request.method=="POST":
        body=request.get_json(force=True)
        availability_input = body.get('availability', {})

        DoctorAvailability.query.filter_by(doctor_id=doctor_id).delete()

        for d in dates:
            dstr=d.strftime("%Y-%m-%d")
            slot_names = availability_input.get(dstr, [])
            for slot_name in slot_names:
                if slot_name not in SLOTS:
                    continue
                start_time, end_time = SLOTS[slot_name]
                da = DoctorAvailability(
                    doctor_id=doctor_id,
                    date=d,
                    slot_name=slot_name,
                    start_time=start_time,
                    end_time=end_time
                )
                db.session.add(da)
        db.session.commit()
        delete_cache(f"doctor:availability:{doctor_id}")

        return success(message="Availability updated successfully")
    
    slots_map = {d.strftime("%Y-%m-%d"): {s: False for s in SLOTS} for d in dates}
    existing  = DoctorAvailability.query.filter_by(doctor_id=doctor_id).all()

    for av in existing:
        dstr = av.date.strftime("%Y-%m-%d")
        if dstr in slots_map and av.slot_name in slots_map[dstr]:
            slots_map[dstr][av.slot_name] = True

    return success({
        "dates":     [d.isoformat() for d in dates],
        "slots":     {k: {"start": v[0].strftime("%H:%M"), "end": v[1].strftime("%H:%M")} for k, v in SLOTS.items()},
        "slots_map": slots_map,
    })

