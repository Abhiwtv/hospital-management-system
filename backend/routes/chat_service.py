from flask import request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from models import db, Appointment, ChatMessage
from utils import success, error, serialize_chat_message

chat_bp = Blueprint('chat', __name__)

def parse_identity(identity_str):
    role, uid_str = identity_str.split(':')
    return role, int(uid_str)
    

def chat_read_guard(appt, uid, role):
    if role == 'doctor' and uid != appt.doctor_id:
        return error("Unauthorized", 403)
    if role == 'patient' and uid != appt.patient_id:
        return error("Unauthorized", 403)
    if role not in ('doctor', 'patient'):
        return error("Unauthorized", 403)
    if appt.status != 'COMPLETED':
        return error("Chat is only available for completed appointments", 403)
    return None

def chat_write_guard(appt, uid, role):
    read_check = chat_read_guard(appt, uid, role)
    if read_check:
        return read_check
    if getattr(appt, 'chat_closed', False):
        return error("This chat has been closed by the doctor", 403)
    
    completed_at = appt.updated_at or datetime.combine(appt.date, datetime.min.time())
    if datetime.now() > completed_at + timedelta(hours=48):
        return error("The 48-hour follow-up window has closed", 403)
    return None

@chat_bp.route('/api/appointments/<int:app_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(app_id):
    appt      = Appointment.query.get_or_404(app_id)
    role, uid = parse_identity(get_jwt_identity())

    if not role or not uid:
        return error("Invalid token format", 401)

    guard = chat_read_guard(appt, uid, role) 
    if guard:
        return guard

    messages = ChatMessage.query.filter_by(appointment_id=app_id).order_by(
        ChatMessage.created_at.asc()
    ).all()

    can_write = chat_write_guard(appt, uid, role) is None

    return success({
        "messages":  [serialize_chat_message(m) for m in messages],
        "chat_open": can_write,
    })


@chat_bp.route('/api/appointments/<int:app_id>/messages', methods=['POST'])
@jwt_required()
def send_message(app_id):
    appt      = Appointment.query.get_or_404(app_id)
    role, uid = parse_identity(get_jwt_identity())

    if not role or not uid:
        return error("Invalid token format", 401)

    guard = chat_write_guard(appt, uid, role) 
    if guard:
        return guard

    sender_role = "DOCTOR" if role == 'doctor' else "PATIENT"
    body        = request.get_json(force=True)
    message     = body.get('message', '').strip()

    if not message:
        return error("Message cannot be empty")

    msg = ChatMessage(
        appointment_id=app_id,
        sender_role=sender_role,
        sender_id=uid,
        message=message,
    )
    db.session.add(msg)
    db.session.commit()
    return success(serialize_chat_message(msg), "Message sent", 201)


@chat_bp.route('/api/doctor/appointments/<int:app_id>/close-chat', methods=['POST'])
@jwt_required()
def close_chat(app_id):
    role, uid = parse_identity(get_jwt_identity())

    if role != 'doctor':
        return error("Authentication required", 403)

    appt = Appointment.query.get_or_404(app_id)

    if appt.doctor_id != uid:
        return error("Unauthorized", 403)

    if appt.status != 'COMPLETED':
        return error("Can only close chat on completed appointments", 400)

    appt.chat_closed = True
    db.session.commit()

    return success(message="Chat closed successfully")