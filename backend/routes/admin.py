from flask import request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db,Department, Doctor, Patient, Appointment
from cache import delete_cache, set_cache, get_cache
from utils import success, error, serialize_doctor, serialize_patient, serialize_appointment,serialize_department

admin_bp=Blueprint('admin', __name__)

@admin_bp.route('/api/admin/dashboard',methods=["GET"])
@jwt_required()
def admin_dashboard():
    identity=get_jwt_identity()
    if identity != "admin":
        return error("Unauthorized", 403)
    doctors=Doctor.query.all()
    patients=Patient.query.all()
    appointments=Appointment.query.order_by(Appointment.date.asc()).limit(10).all()

    return success({
        "doctors": [serialize_doctor(d) for d in doctors],
        "patients": [serialize_patient(p) for p in patients],
        "recent_appointments": [serialize_appointment(a) for a in appointments]
    })

@admin_bp.route('/api/admin/doctors',methods=["GET","POST"])
@jwt_required()
def admin_doctors():
    identity=get_jwt_identity()
    if identity!="admin":
        return error("Unauthorized",403)
    if request.method=="GET":
        cached=get_cache("doctors:list")
        if cached:
            return success({"doctors": cached},"Doctors fetched from cache")
        doctors=Doctor.query.all()
        doc_data=[serialize_doctor(d) for d in doctors]
        set_cache("doctors:list",doc_data)
        return success({"doctors": doc_data},"Doctors fetched from database")
    
    
    body       = request.get_json(force=True)
    username   = body.get('username')
    name       = body.get('name')
    password   = body.get('password')
    dtype      = body.get('type')
    dep_id     = body.get('dep_id')
    email      = body.get('doctor_email')

    if Doctor.query.filter_by(doctor_username=username).first():
        return error("Username already exists")

    if Doctor.query.filter_by(doctor_email=email).first():
        return error("Email already exists")

    new_doc = Doctor(
        doctor_username=username,
        doctor_name=name,
        doctor_email=email,
        doctor_pass=password,
        doctor_type=dtype,
        doctor_qualification=body.get('qualification'),
        doctor_experience=body.get('experience'),
        doctor_description=body.get('description'),
        dep_id=dep_id,
    )
    db.session.add(new_doc)
    if dep_id:
        department = Department.query.get(dep_id)
        if not department:
            return error("Department not found")
        department.no_docs_registered=(department.no_docs_registered or 0)+1
    db.session.commit()
    delete_cache("doctors:list")
    if dep_id:
        delete_cache("department:list")
        delete_cache(f"department:{dep_id}")
    return success({"doctor": serialize_doctor(new_doc)}, "Doctor added successfully",201)
    
@admin_bp.route('/api/admin/doctors/<int:doctor_id>',methods=["GET","PUT","DELETE"])
@jwt_required()
def admin_doctor_detail(doctor_id):
    identity=get_jwt_identity()
    if identity!="admin":
        return error("Unauthorized",403)
    doctor=Doctor.query.get(doctor_id)
    if not doctor:
        return error("Doctor not found",404)
    if request.method=="GET":
        return success({"doctor":serialize_doctor(doctor)},"Doctor details fetched successfully")
    if request.method=="PUT":
        body=request.get_json(force=True)
        new_dep_id     = body.get('dep_id', doctor.dep_id)
        dep_id_changed = new_dep_id != doctor.dep_id

        if dep_id_changed:
            if doctor.dep_id:
                old_dept = Department.query.get(doctor.dep_id)
                if old_dept:
                    old_dept.no_docs_registered = max(0, (old_dept.no_docs_registered or 1) - 1)
            if new_dep_id:
                new_dept = Department.query.get(new_dep_id)
                if not new_dept:
                    return error(f"Department with id {new_dep_id} does not exist")
                new_dept.no_docs_registered = (new_dept.no_docs_registered or 0) + 1

        old_dep_id= doctor.dep_id

        doctor.doctor_username    = body.get('username',doctor.doctor_username)
        doctor.doctor_name        = body.get('name',          doctor.doctor_name)
        doctor.doctor_pass        = body.get('password',      doctor.doctor_pass)
        doctor.doctor_type        = body.get('type',          doctor.doctor_type)
        doctor.doctor_qualification = body.get('qualification', doctor.doctor_qualification)
        doctor.doctor_experience  = body.get('experience',    doctor.doctor_experience)
        doctor.doctor_description = body.get('description',   doctor.doctor_description)
        doctor.doctor_email       = body.get('email',         doctor.doctor_email)
        doctor.dep_id             = new_dep_id
        db.session.commit()

        delete_cache("doctors:list")
        delete_cache(f"doctor:availability:{doctor_id}") 
        if dep_id_changed:
            delete_cache("departments:list")
            if old_dep_id:
                delete_cache(f"department:{old_dep_id}")
            if new_dep_id:
                delete_cache(f"department:{new_dep_id}")

        return success(serialize_doctor(doctor), "Doctor updated successfully")
    
    old_dep_id = doctor.dep_id

    if old_dep_id:
        dept = Department.query.get(old_dep_id)
        if dept:
            dept.no_docs_registered = max(0, (dept.no_docs_registered or 1) - 1)

    db.session.delete(doctor)
    db.session.commit()

    delete_cache("doctors:list")
    delete_cache(f"doctor:availability:{doctor_id}")
    if old_dep_id:
        delete_cache("departments:list")
        delete_cache(f"department:{old_dep_id}")

    return success(message="Doctor deleted successfully")

@admin_bp.route('/api/admin/doctors/search',methods=["GET"])
@jwt_required()
def admin_search_doctors():
    identity=get_jwt_identity()
    if identity!="admin":
        return error("Unauthorized",403)
    q=request.args.get("q","").strip()
    doctors=Doctor.query.filter(Doctor.doctor_name.ilike(f'%{q}%')).all()
    return success({"doctors":[serialize_doctor(d) for d in doctors]},"Search results")

@admin_bp.route('/api/admin/patients',methods=["GET"])
@jwt_required()
def admin_patients():
    identity=get_jwt_identity()
    if identity!="admin":
        return error("Unauthorized",403)
    cached=get_cache("patients:list")
    if cached:
        return success({"patients": cached},"Patients fetched from cache")
    patients=Patient.query.all()
    pat_data=[serialize_patient(p) for p in patients]
    set_cache("patients:list",pat_data)
    return success({"patients": pat_data},"Patients fetched from database")

@admin_bp.route('/api/admin/patients/<int:patient_id>',methods=["GET","DELETE"])
@jwt_required()
def admin_patient_detail(patient_id):
    identity=get_jwt_identity()
    if identity!="admin":
        return error("Unauthorized",403)
    patient=Patient.query.get(patient_id)
    if not patient:
        return error("Patient not found",404)
    if request.method=="GET":
        appointments=Appointment.query.filter_by(patient_id=patient_id).all()
        return success({"patient":serialize_patient(patient),"appointments":[serialize_appointment(a,include_treatment=True) for a in appointments]},"Patient details fetched successfully")
    
    db.session.delete(patient)
    db.session.commit()

    delete_cache("patients:list")
    return success(message="Patient blacklisted successfully")

@admin_bp.route('/api/admin/patients/<int:patient_id>/history',methods=["GET"])
@jwt_required()
def admin_patient_history(patient_id):
    identity=get_jwt_identity()
    if identity!="admin":
        return error("Unauthorized",403)
    patient=Patient.query.get_or_404(patient_id)
    appointments=Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.date.desc()).all()
    return success({
        "patient":      serialize_patient(patient),
        "appointments": [serialize_appointment(a, include_treatment=True) for a in appointments],
    })

@admin_bp.route('/api/admin/patients/<int:patient_id>/blacklist', methods=['POST'])
@jwt_required()
def admin_blacklist_patient(patient_id):
    identity = get_jwt_identity()
    if identity != 'admin':
        return error("Admin authentication required", 403)

    patient = Patient.query.get_or_404(patient_id)
    patient.is_blacklisted = True
    db.session.commit()
    delete_cache("patients:list")

    return success(serialize_patient(patient), "Patient blacklisted successfully")


@admin_bp.route('/api/admin/patients/<int:patient_id>/unblacklist', methods=['POST'])
@jwt_required()
def admin_unblacklist_patient(patient_id):
    identity = get_jwt_identity()
    if identity != 'admin':
        return error("Admin authentication required", 403)

    patient = Patient.query.get_or_404(patient_id)
    patient.is_blacklisted = False
    db.session.commit()
    delete_cache("patients:list")

    return success(serialize_patient(patient), "Patient unblacklisted successfully")

@admin_bp.route('/api/admin/departments',methods=["GET","POST"])
@jwt_required()
def admin_departments():
    identity=get_jwt_identity()
    if identity!="admin":
        return error("Unauthorized",403)
    if request.method=="GET":
        cached=get_cache("departments:list")
        if cached:
            return success({"departments": cached},"Departments fetched from cache")
        departments=Department.query.all()
        data=[serialize_department(d) for d in departments]
        set_cache("departments:list",data)
        return success({"departments": data},"Departments fetched from database")

    body     = request.get_json(force=True)
    dep_name = body.get('dep_name')
    if not dep_name:
        return error("Department name is required")

    dept = Department(
        dep_name=dep_name,
        dep_des=body.get('dep_des'),
        no_docs_registered=0,
    )
    db.session.add(dept)
    db.session.commit()
    delete_cache("departments:list")

    return success(serialize_department(dept), "Department created successfully", 201)

@admin_bp.route('/api/admin/departments/<int:dep_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def admin_department_detail(dep_id):
    identity = get_jwt_identity()
    if identity != 'admin':
        return error("Admin authentication required", 403)

    dept = Department.query.get_or_404(dep_id)

    if request.method == 'GET':
        cache_key = f"department:{dep_id}"
        cached    = get_cache(cache_key)
        if cached:
            return success(cached)

        data = serialize_department(dept)
        set_cache(cache_key, data)
        return success(data)

    if request.method == 'PUT':
        body = request.get_json(force=True)
        dept.dep_name = body.get('dep_name', dept.dep_name)
        dept.dep_des  = body.get('dep_des',  dept.dep_des)
        db.session.commit()

        delete_cache(f"department:{dep_id}")
        delete_cache("departments:list")

        return success(serialize_department(dept), "Department updated successfully")

    
    db.session.delete(dept)
    db.session.commit()

    delete_cache(f"department:{dep_id}")
    delete_cache("departments:list")

    return success(message="Department deleted successfully")

@admin_bp.route('/api/admin/appointments', methods=['GET'])
@jwt_required()
def admin_appointments():
    identity = get_jwt_identity()
    if identity != 'admin':
        return error("Admin authentication required", 403)

    query = Appointment.query

    status     = request.args.get('status')
    doctor_id  = request.args.get('doctor_id', type=int)
    patient_id = request.args.get('patient_id', type=int)

    if status:
        query = query.filter(Appointment.status == status.upper())
    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)

    appointments = query.order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    return success({"appointments": [serialize_appointment(a, include_treatment=True) for a in appointments]})


@admin_bp.route('/api/admin/reminders/trigger', methods=['POST'])
@jwt_required()
def trigger_reminders():
    identity = get_jwt_identity()
    if identity != 'admin':
        return error("Admin authentication required", 403)

    from celery_app import celery  
    task = celery.send_task('tasks.send_daily_reminders')

    return success(
        {"task_id": task.id},
        "Reminder task queued, check your inbox in a few seconds"
    )

@admin_bp.route('/api/admin/reports/trigger', methods=['POST'])
@jwt_required()
def trigger_monthly_report():
    identity = get_jwt_identity()
    if identity != 'admin':
        return error("Admin authentication required", 403)

    from celery_app import celery
    task = celery.send_task('tasks.send_monthly_report')
    return success({"task_id": task.id}, "Monthly report task queued")

@admin_bp.route("/api/admin/users",methods=["GET"])
@jwt_required()
def admin_users():
    identity=get_jwt_identity()
    if identity!="admin":
        return error("Unauthorized",403)
    patients=Patient.query.all()
    return success({"users":[serialize_patient(p) for p in patients]},"Users fetched successfully")

@admin_bp.route("/api/admin/users/<int:patient_id>",methods=["GET"])
@jwt_required()
def admin_user_detail(patient_id):
    identity=get_jwt_identity()
    if identity!="admin":
        return error("Unauthorized",403)
    patient=Patient.query.get(patient_id)
    return success({"user":serialize_patient(patient)},"User details fetched successfully")
