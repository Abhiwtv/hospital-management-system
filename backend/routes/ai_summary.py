import os
from flask import jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from google import genai
from models import Patient, Appointment
from utils import success, error

GEMINI_API_KEY = "AIzaSyA0oqycpprBXwNgp6yMXgqh-H2kvaWV25o"
client = genai.Client(api_key=GEMINI_API_KEY)

ai_summary_bp = Blueprint('ai_summary', __name__)

def build_patient_prompt(patient, appointments):
    lines = [
        f"Patient Name   : {patient.patient_name}",
        f"Age            : {patient.age or 'Unknown'}",
        f"Gender         : {patient.gender or 'Unknown'}",
        f"Total Visits   : {len(appointments)}",
        "Appointment History:",
    ]
 
    completed_with_treatment = [
        a for a in appointments
        if a.status == "COMPLETED" and a.treatment
    ]
 
    if not completed_with_treatment:
        return None  
 
    for a in completed_with_treatment:
        t = a.treatment
        lines.append(f"\nDate           : {a.date.isoformat()}")
        lines.append(f"Doctor         : {a.doctor.doctor_name if a.doctor else 'Unknown'}")
        lines.append(f"Diagnosis      : {t.diagnosis      or 'N/A'}")
        lines.append(f"Prescription   : {t.prescription   or 'N/A'}")
        lines.append(f"Medication     : {t.medication     or 'N/A'}")
        lines.append(f"Tests Done     : {t.tests_done     or 'N/A'}")
        lines.append(f"Next Visit     : {t.next_visit_date.isoformat() if t.next_visit_date else 'N/A'}")
 
    history_text = "\n".join(lines)
 
    prompt = f"""You are a clinical assistant helping a doctor quickly understand a patient's medical history.
 
Below is the structured appointment and treatment history for a patient. 
Write a clear, concise clinical summary in 4–6 sentences.
 
Include:
- How many times the patient has visited and over what period
- Recurring or changing diagnoses
- Medications or treatments that appear across visits
- Any notable trends (improving, worsening, stable)
- The most recent visit details and any next visit recommendations
 
Keep the tone professional and clinical. Do not add any information not present in the data.
 
{history_text}
 
Clinical Summary:"""
 
    return prompt

@ai_summary_bp.route('/api/doctor/patients/<int:patient_id>/summary', methods=['POST'])
@jwt_required()
def generate_patient_summary(patient_id):
    identity = get_jwt_identity()
    try:
        role, did_str = identity.split(":")
        if role != 'doctor':
            return error("Doctor authentication required", 403)
    except (ValueError, AttributeError):
        return error("Invalid token format", 401)
 
    patient = Patient.query.get_or_404(patient_id)
 
    appointments = Appointment.query.filter_by(
        patient_id=patient_id
    ).order_by(Appointment.date.asc()).all()
 
    prompt = build_patient_prompt(patient, appointments)
 
    if not prompt:
        return error(
            "Not enough treatment history to generate a summary. "
            "The patient needs at least one completed appointment with treatment recorded.",
            400
        )
 
    # Call Gemini Flash
    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt,
        )
        summary = response.text.strip()
 
        return success({"summary": summary}, "Summary generated successfully")
 
    except Exception as e:
        print(f"[Gemini] Error: {e}")
        return error(
            "Failed to generate summary check your GEMINI_API_KEY and internet connection.",
            503
        )

@ai_summary_bp.route('/api/debug/models', methods=['GET'])
def list_models():
    models = [m.name for m in client.models.list()]
    return jsonify(models)