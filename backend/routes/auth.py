from utils import success, error, serialize_doctor, serialize_patient
from models import db, Doctor, Patient
from cache import delete_cache,blacklist_token
from flask import request,Blueprint
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt, set_refresh_cookies, unset_jwt_cookies)

from datetime import datetime, timezone

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/login/doctor', methods=['POST'])
def doctor_login():
    body     = request.get_json(force=True)
    username = body.get('username')
    password = body.get('password')

    doctor = Doctor.query.filter_by(doctor_username=username).first()
    if not doctor or doctor.doctor_pass != password:
        return error("Invalid username or password", 401)

    identity_str = f"doctor:{doctor.doctor_id}"
    
    access_token  = create_access_token(identity=identity_str)
    refresh_token = create_refresh_token(identity=identity_str)

    response= success({
        "doctor":       serialize_doctor(doctor),
        "access_token":  access_token, 
    }, "Login successful")

    
    resp = response[0] 

    set_refresh_cookies(resp, refresh_token)

    return resp, response[1]

@auth_bp.route('/api/auth/login/admin', methods=["POST"])
def admin_login():
    body=request.get_json(force=True)
    username=body.get("username")
    password=body.get("password")

    if username=='admin' and password=='admin123':
        access_token=create_access_token(identity="admin")
        refresh_token=create_refresh_token(identity="admin")

        response=success({"user_type":"admin", "access_token": access_token},"Admin Login Success")
        resp=response[0]
        set_refresh_cookies(resp, refresh_token)
        return resp, response[1]
    
    return error("Invalid admin credentials", 401)

@auth_bp.route('/api/auth/register/patient', methods=["POST"])
def patient_register():
    body=request.get_json(force=True)
    name=body.get("name")
    username=body.get("username")
    email=body.get("email")
    password=body.get("password")
    address=body.get("address")
    phone=body.get("phone")
    gender=body.get("gender")
    age=body.get("age")


    if Patient.query.filter_by(patient_username=username).first():
        return error("Username already exists")

    if Patient.query.filter_by(email=email).first():
        return error("Email already exists")

    new_patient = Patient(
        patient_name=name,
        patient_username=username,
        patient_pass=password,
        email=email,
        address=address,
        phone=phone,
        gender=gender,
        age=age
    )
    db.session.add(new_patient)
    db.session.commit()

    return success({"patient": serialize_patient(new_patient)}, "Patient registered successfully", 201)

@auth_bp.route('/api/auth/login/patient',methods=["POST"])
def patient_login():
    body=request.get_json(force=True)
    username=body.get("username")
    password=body.get("password")

    patient=Patient.query.filter_by(patient_username=username).first()
    if not patient or patient.patient_pass!=password:
        return error("Invalid username or password", 401)
    if patient.is_blacklisted:
        return error("Your account has been blacklisted. Please contact support.", 403)
    identity_str=f"patient:{patient.patient_id}"

    access_token=create_access_token(identity=identity_str)
    refresh_token=create_refresh_token(identity=identity_str)

    response=success({"patient":serialize_patient(patient), "access_token":access_token}, "Patient Login Success")
    resp=response[0]
    set_refresh_cookies(resp,refresh_token)
    return resp, response[1]

@auth_bp.route('/api/auth/logout',methods=["POST"])
@jwt_required()
def logout():
    jwt_data=get_jwt()
    access_timeleft=max(1,int(jwt_data['exp']-datetime.now(timezone.utc).timestamp()))
    blacklist_token(jwt_data['jti'],access_timeleft)

    response=success(message="Logout successful")
    resp=response[0]
    unset_jwt_cookies(resp)
    return resp,response[1]

@auth_bp.route('/api/auth/me', methods=['GET'])
@jwt_required()
def auth_me():
    identity = get_jwt_identity()

    if identity == 'admin':
        return success({"role": "admin", "user_type": "admin"})

    try:
        role, uid = identity.split(":")
        uid = int(uid)
    except ValueError:
        return error("Invalid token format", 401)

    if role == 'doctor':
        doctor = Doctor.query.get(uid)
        if not doctor:
            return error("User not found", 404)
        return success({"role": "doctor", **serialize_doctor(doctor)})

    if role == 'patient':
        patient = Patient.query.get(uid)
        if not patient:
            return error("User not found", 404)
        return success({"role": "patient", **serialize_patient(patient)})

    return error("Invalid token", 401)