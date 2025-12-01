# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ------------------- User Model -------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # Relationships
    applications = db.relationship('Application', backref='applicant', lazy=True)

# ------------------- Job Model -------------------
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    posted_on = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    applications = db.relationship('Application', backref='job', lazy=True)

# ------------------- Application Model -------------------
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    resume = db.Column(db.String(200), nullable=False)
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed = db.Column(db.Boolean, default=False)
