from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from datetime import timedelta
from models import db, Doctor
from cache import is_token_blacklisted
from celery_app import celery as celery_app

from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.doctor import doc_bp
from routes.patient import pat_bp
from routes.ai_summary import ai_summary_bp
from routes.chat_service import chat_bp

app = Flask(__name__)
CORS(app, supports_credentials=True) 


app.config['SECRET_KEY']              = os.environ.get('SECRET_KEY', 'dev_secret_change_in_prod')
app.config['JWT_SECRET_KEY']          = "super_secret_key_that_is_longer_than_32_characters_for_security"
app.config['JWT_ACCESS_TOKEN_EXPIRES']  = timedelta(minutes=15)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies'] 
app.config['JWT_COOKIE_SECURE']  = False 
app.config['JWT_COOKIE_CSRF_PROTECT'] = True 

celery_app.conf.update(app.config)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'hospital.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return is_token_blacklisted(jwt_payload['jti'])

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(doc_bp)
app.register_blueprint(pat_bp)
app.register_blueprint(ai_summary_bp)
app.register_blueprint(chat_bp)

with app.app_context():
    db.create_all()
    if not Doctor.query.filter_by(doctor_username='admin').first():
        admin = Doctor(
            doctor_username='admin',
            doctor_name='Super Admin',
            doctor_pass='admin123',
            doctor_type='Admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("Super Admin created successfully.")

if __name__ == '__main__':
    app.run(debug=True)