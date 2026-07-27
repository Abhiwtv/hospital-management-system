from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Enum

db = SQLAlchemy()


class Department(db.Model):
    __tablename__ = "departments"

    dep_id = db.Column(db.Integer, primary_key=True)
    dep_name = db.Column(db.String(100), nullable=False)
    dep_des = db.Column(db.Text)
    no_docs_registered = db.Column(db.Integer, default=0)

    
    doctors = db.relationship(
        "Doctor",
        back_populates="department",
        foreign_keys="Doctor.dep_id",
        cascade="all, delete-orphan"
    )

   



class Doctor(db.Model):
    __tablename__ = "doctors"

    doctor_id = db.Column(db.Integer, primary_key=True)
    doctor_username = db.Column(db.String(50), unique=True, nullable=False)
    doctor_name = db.Column(db.String(100), nullable=False)
    doctor_pass = db.Column(db.String(255), nullable=False)
    doctor_description = db.Column(db.Text)
    doctor_email = db.Column(db.String(120), nullable=True)
    dep_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.dep_id", ondelete="SET NULL"),
        nullable=True
    )

    doctor_qualification = db.Column(db.String(100))
    doctor_experience = db.Column(db.Integer)
    doctor_type = db.Column(db.String(50))


    
    department = db.relationship(
        "Department",
        back_populates="doctors",
        foreign_keys=[dep_id]
    )

    availabilities = db.relationship(
        "DoctorAvailability",
        back_populates="doctor",
        cascade="all, delete-orphan"
    )

    
    appointments = db.relationship(
        "Appointment",
        back_populates="doctor",
        cascade="all, delete-orphan"
    )

class DoctorAvailability(db.Model):
    __tablename__ = "doctor_availabilities"

    availability_id = db.Column(db.Integer, primary_key=True)

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.doctor_id", ondelete="CASCADE"),
        nullable=False
    )

    date = db.Column(db.Date, nullable=False)
    slot_name = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)


    doctor = db.relationship("Doctor", back_populates="availabilities")


class Patient(db.Model):
    __tablename__ = "patients"

    patient_id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    patient_username = db.Column(db.String(50), unique=True, nullable=False)
    patient_pass = db.Column(db.String(255), nullable=False)

    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    address = db.Column(db.Text)

    is_blacklisted = db.Column(db.Boolean, default=False)

    

    appointments = db.relationship(
        "Appointment",
        back_populates="patient",
        cascade="all, delete-orphan"
    )


class Appointment(db.Model):
    __tablename__ = "appointments"

    app_id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.patient_id", ondelete="CASCADE"),
        nullable=False
    )

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.doctor_id", ondelete="CASCADE"),
        nullable=False
    )

    status = db.Column(
    Enum("BOOKED", "COMPLETED", "CANCELLED", name="appointment_status"),
    nullable=False,
    default="BOOKED",
    index=True
    )
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    visit_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
    db.DateTime,
    default=datetime.utcnow,
    onupdate=datetime.utcnow
)
    chat_closed = db.Column(db.Boolean, default=False)

    treatment = db.relationship(
        "Treatment",
        back_populates="appointment",
        cascade="all, delete-orphan",
        uselist=False
    )

    patient = db.relationship("Patient", back_populates="appointments")
    doctor = db.relationship("Doctor", back_populates="appointments")


    chat_messages = db.relationship(
    "ChatMessage",
    backref="appointment",
    cascade="all, delete-orphan",
    order_by="ChatMessage.created_at"
)




    @property
    def department(self):
        return self.doctor.department if self.doctor else None



class Treatment(db.Model):
    __tablename__ = "treatments"

    treatment_id = db.Column(db.Integer, primary_key=True)

    app_id = db.Column(
        db.Integer,
        db.ForeignKey("appointments.app_id", ondelete="CASCADE"),
        nullable=False
    )

    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    medication = db.Column(db.Text)
    tests_done = db.Column(db.Text)
    next_visit_date = db.Column(db.Date)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointment = db.relationship("Appointment", back_populates="treatment")


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)

    appointment_id = db.Column(
        db.Integer,
        db.ForeignKey("appointments.app_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    sender_role = db.Column(
        db.Enum("DOCTOR", "PATIENT", name="sender_role_enum"),
        nullable=False
    )

    sender_id = db.Column(db.Integer, nullable=False)

    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        index=True
    )
