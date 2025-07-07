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
    
    # New profile fields
    profile_picture = db.Column(db.String(255), nullable=True, default='default-avatar.png')
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    education_level = db.Column(db.String(50), nullable=True)
    school_name = db.Column(db.String(100), nullable=True)
    internship_start_date = db.Column(db.Date, nullable=True)
    internship_end_date = db.Column(db.Date, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Profile settings
    is_profile_complete = db.Column(db.Boolean, default=False)
    notification_enabled = db.Column(db.Boolean, default=True)
    theme_preference = db.Column(db.String(10), default='light')

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

class ProfileChangeLog(db.Model):
    __tablename__ = 'profile_change_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    field_changed = db.Column(db.String(50), nullable=False)
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)
    
    student = db.relationship('Student', backref=db.backref('profile_changes', lazy=True))

    def __repr__(self):
        return f'<ProfileChangeLog {self.student_id}:{self.field_changed}>'