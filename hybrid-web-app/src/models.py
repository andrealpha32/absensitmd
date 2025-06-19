from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    supervisor = db.Column(db.String(100), nullable=True)
    company = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<Student {self.name}>'

class Attendance(db.Model):
    __tablename__ = 'attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    time_in = db.Column(db.Time, nullable=False)
    time_out = db.Column(db.Time, nullable=True)
    activity = db.Column(db.Text, nullable=False)
    attendance_type = db.Column(db.String(20), nullable=False, default='masuk')  # masuk, izin, sakit
    photo_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False)
    
    student = db.relationship('Student', backref=db.backref('attendances', lazy=True))
    time_out = db.Column(db.Time, nullable=True)
    activity = db.Column(db.Text, nullable=False)
    attendance_type = db.Column(db.String(20), nullable=False, default='masuk')  # masuk, izin, sakit
    photo_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False)
    
    student = db.relationship('Student', backref=db.backref('attendances', lazy=True))

class AttendanceSummary(db.Model):
    __tablename__ = 'attendance_summaries'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    present_count = db.Column(db.Integer, default=0)
    sick_count = db.Column(db.Integer, default=0)
    excused_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AttendanceSummary {self.date}>'
