from flask import jsonify 

def success(data=None, message="OK", status=200):
    body = {"success": True, "message": message}
    if data is not None:
        body["data"] = data
    return jsonify(body), status


def error(message, status=400):
    return jsonify({"success": False, "message": message}), status


def serialize_doctor(d):
    return {
        "doctor_id":          d.doctor_id,
        "doctor_username":    d.doctor_username,
        "doctor_name":        d.doctor_name,
        "doctor_type":        d.doctor_type,
        "doctor_qualification": d.doctor_qualification,
        "doctor_experience":  d.doctor_experience,
        "doctor_description": d.doctor_description,
        "dep_id":             d.dep_id,
        "department_name":    d.department.dep_name if d.department else None,
        "doctor_email":       d.doctor_email,
    }


def serialize_patient(p):
    return {
        "patient_id":       p.patient_id,
        "patient_name":     p.patient_name,
        "patient_username": p.patient_username,
        "email":            p.email,
        "phone":            p.phone,
        "gender":           p.gender,
        "age":              p.age,
        "address":          p.address,
        "is_blacklisted":   p.is_blacklisted,
    }


def serialize_appointment(a, include_treatment=False):
    from datetime import datetime as _dt, timedelta as _td

    completed_at = a.updated_at or _dt.combine(a.date, _dt.min.time())
    cutoff       = completed_at + _td(hours=48)
    chat_open    = (
        a.status == 'COMPLETED'
        and _dt.now() <= cutoff
        and not getattr(a, 'chat_closed', False)
    )

    data = {
        "app_id":       a.app_id,
        "patient_id":   a.patient_id,
        "patient_name": a.patient.patient_name if a.patient else None,
        "doctor_id":    a.doctor_id,
        "doctor_name":  a.doctor.doctor_name if a.doctor else None,
        "status":       a.status,
        "date":         a.date.isoformat(),
        "time":         a.time.strftime("%H:%M"),
        "visit_type":   a.visit_type,
        "created_at":   a.created_at.isoformat() if a.created_at else None,
        "updated_at":   a.updated_at.isoformat() if a.updated_at else None,
        "chat_closed":  getattr(a, 'chat_closed', False),
        "chat_open":    chat_open,
    }
    if include_treatment:
        data["treatment"] = serialize_treatment(a.treatment) if a.treatment else None
    return data

def serialize_treatment(t):
    if not t:
        return None
    return {
        "treatment_id":    t.treatment_id,
        "diagnosis":       t.diagnosis,
        "prescription":    t.prescription,
        "medication":      t.medication,
        "tests_done":      t.tests_done,
        "next_visit_date": t.next_visit_date.isoformat() if t.next_visit_date else None,
        "created_at":      t.created_at.isoformat() if t.created_at else None,
    }


def serialize_department(d):
    return {
        "dep_id":              d.dep_id,
        "dep_name":            d.dep_name,
        "dep_des":             d.dep_des,
        "no_docs_registered":  d.no_docs_registered,
    }


def serialize_chat_message(m):
    return {
        "id":             m.id,
        "appointment_id": m.appointment_id,
        "sender_role":    m.sender_role,
        "sender_id":      m.sender_id,
        "message":        m.message,
        "created_at":     m.created_at.isoformat() if m.created_at else None,
    }


def serialize_availability(av):
    return {
        "availability_id": av.availability_id,
        "doctor_id":       av.doctor_id,
        "date":            av.date.isoformat(),
        "slot_name":       av.slot_name,
        "start_time":      av.start_time.strftime("%H:%M"),
        "end_time":        av.end_time.strftime("%H:%M"),
    }


