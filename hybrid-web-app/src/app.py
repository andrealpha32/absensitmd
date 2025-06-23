from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
from models import db, Student, Attendance, AttendanceSummary
from config import Config
from sqlalchemy import case
import logging
import os
import calendar
import schedule
import time

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except ImportError:
    from pytz import timezone as ZoneInfo  # fallback jika pakai pytz

app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db.init_app(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add hardcoded admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Log the login attempt
        logger.debug(f"Login attempt for email: {email}")
        
        if not email or not password:
            flash('Mohon isi email dan password', 'danger')
            return render_template('login.html')
            
        # Find the student and log the result
        student = Student.query.filter_by(email=email).first()
        if student:
            logger.debug(f"Found student: {student.name}, checking password")
            # Check if passwords match exactly
            if student.password == password:
                session['logged_in'] = True
                session['student_id'] = student.id
                session['student_name'] = student.name  # Add name to session for convenience
                logger.debug(f"Login successful for student: {student.name}")
                flash('Login berhasil!', 'success')
                return redirect(url_for('dashboard'))
            else:
                logger.debug("Password mismatch")
                flash('Password salah!', 'danger')
        else:
            logger.debug("Student not found with provided email")
            flash('Email tidak terdaftar!', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            # Enhanced validation
            if not all([name, email, password, confirm_password]):
                flash('Semua field harus diisi!', 'danger')
                return render_template('register.html')

            if len(password) < 6:
                flash('Password harus minimal 6 karakter!', 'danger')
                return render_template('register.html')

            if Student.query.filter_by(email=email).first():
                flash('Email sudah terdaftar!', 'danger')
                return render_template('register.html')

            if password != confirm_password:
                flash('Password tidak cocok!', 'danger')
                return render_template('register.html')

            # Create new student
            new_student = Student(
                name=name,
                email=email,
                password=password
            )
            
            db.session.add(new_student)
            db.session.commit()
            
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error during registration: {str(e)}")
            flash('Terjadi kesalahan saat registrasi!', 'danger')
    
    return render_template('register.html')

def get_today_attendance(student_id):
    student = db.session.get(Student, student_id)  # Updated from query.get()
    if not student:
        return None
    
    return Attendance.query.filter_by(
        student_id=student.id,
        date=datetime.now(timezone.utc).date()  # Updated to use timezone-aware datetime
    ).first()

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    student = db.session.get(Student, session['student_id'])  # Updated from query.get()
    
    # Get current month calendar data
    current_date = datetime.now(timezone.utc)  # Using timezone-aware datetime
    cal = calendar.monthcalendar(current_date.year, current_date.month)
    today = current_date.date()
    
    # Get attendance summaries for current month
    summaries = AttendanceSummary.query.filter(
        db.extract('month', AttendanceSummary.date) == today.month,
        db.extract('year', AttendanceSummary.date) == today.year
    ).all()
    
    # Format calendar data
    calendar_data = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append({'date': ''})
                continue
                
            date = datetime(today.year, today.month, day, tzinfo=timezone.utc).date()
            summary = next((s for s in summaries if s.date == date), None)
            
            week_data.append({
                'date': day,
                'today': date == today,
                'past': date < today,
                'summary': summary
            })
        calendar_data.append(week_data)
    
    return render_template('dashboard.html',
                         student=student,
                         attendance=get_today_attendance(session['student_id']),
                         calendar_data=calendar_data,
                         current_month=current_date.strftime('%B %Y'))

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if not session.get('logged_in'):
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    student_id = session.get('student_id')
    if not student_id:
        flash('Session invalid, please login again', 'warning')
        return redirect(url_for('logout'))
    
    student = Student.query.get(student_id)
    if not student:
        flash('Student not found, please login again', 'warning')
        return redirect(url_for('logout'))
    
    # Gunakan zona waktu Asia/Jakarta
    WIB = ZoneInfo('Asia/Jakarta')
    now_wib = datetime.now(WIB)
    today = now_wib.date()
    
    # Check if student has already attended today
    existing_attendance = Attendance.query.filter_by(
        student_id=student_id,
        date=today
    ).first()
    
    if existing_attendance:
        flash('Anda sudah melakukan absensi hari ini!', 'warning')
        return redirect(url_for('dashboard'))
    
    current_time = now_wib.time()
    start_time = datetime.strptime('08:00', '%H:%M').time()
    end_time = datetime.strptime('17:00', '%H:%M').time()
    if not (start_time <= current_time <= end_time):
        flash('Absensi hanya dapat dilakukan antara pukul 08:00 sampai 17:00 WIB!', 'warning')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        activity = request.form.get('activity')
        attendance_type = request.form.get('attendance_type')
        now = now_wib  # gunakan waktu WIB
        
        # Handle file upload
        photo = request.files.get('photo')
        photo_path = None
        
        if photo and allowed_file(photo.filename):
            filename = f"{session['student_id']}_{now.strftime('%Y%m%d_%H%M%S')}.{photo.filename.rsplit('.', 1)[1]}"
            photo_path = f"uploads/{filename}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(save_path)
        
        attendance = Attendance(
            student_id=session['student_id'],
            date=today,
            time_in=now.time(),
            activity=activity,
            attendance_type=attendance_type,
            photo_path=photo_path,
            status=attendance_type
        )
        
        db.session.add(attendance)
        db.session.commit()
        flash('Absensi berhasil dicatat!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('attendance.html')

@app.route('/history')
def history():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    student = Student.query.get(session['student_id'])
    attendances = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.date.desc()).all()
    return render_template('history.html', attendances=attendances)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Use hardcoded credentials instead of database
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Login berhasil!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        flash('Username atau password salah!', 'danger')
    
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Add year and month to template variables
    now = datetime.now()
    today = now.date()
    year = int(request.args.get('year', now.year))
    month = int(request.args.get('month', now.month))
    
    # Get calendar data with detailed student attendance for all days
    cal = calendar.monthcalendar(year, month)
    
    # Get all attendance records for the month
    month_attendance = db.session.query(
        Attendance.date,
        Attendance.status,
        Student
    ).join(Student).filter(
        db.extract('year', Attendance.date) == year,
        db.extract('month', Attendance.date) == month
    ).all()

    # Group attendance by date
    attendance_by_date = {}
    for attendance in month_attendance:
        date = attendance.date
        if date not in attendance_by_date:
            attendance_by_date[date] = {
                'hadir': 0,
                'sakit': 0,
                'izin': 0,
                'students': []
            }
        attendance_by_date[date][attendance.status] += 1
        attendance_by_date[date]['students'].append({
            'name': attendance.Student.name,
            'status': attendance.status
        })

    # Format calendar data
    calendar_data = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append({'date': ''})
                continue
                
            date = datetime(year, month, day).date()
            attendance_data = attendance_by_date.get(date, {
                'hadir': 0,
                'sakit': 0,
                'izin': 0,
                'students': []
            })
            day_data = {
                'date': day,
                'today': date == today,
                'past': date < today,
                'attendance': attendance_data if attendance_data['hadir'] > 0 or attendance_data['sakit'] > 0 or attendance_data['izin'] > 0 else None
            }
            week_data.append(day_data)
        calendar_data.append(week_data)

    # Get all students and their attendance for today
    today_attendance = db.session.query(
        Student,
        Attendance
    ).outerjoin(
        Attendance,
        db.and_(
            Attendance.student_id == Student.id,
            Attendance.date == today
        )
    ).order_by(Student.name).all()  # Order by student name for consistent display

    # Format today's students data
    students_today = []
    for student, attendance in today_attendance:
        student_data = {
            'id': student.id,
            'name': student.name,
            'email': student.email,
            'company': 'Trimediatama',
            'attendance_status': attendance.status if attendance else 'Belum Absen',
            'time_in': attendance.time_in.strftime('%H:%M') if attendance and attendance.time_in else None,
            'activity': attendance.activity if attendance else None,
            'photo_path': attendance.photo_path if attendance and attendance.photo_path else None
        }
        students_today.append(student_data)

    # Get basic statistics
    statistics = {
        'total_students': Student.query.count(),
        'today_attendance': Attendance.query.filter_by(date=today).count(),
        'total_attendance': len(month_attendance)
    }

    return render_template('admin/dashboard.html',
                         calendar_data=calendar_data,
                         current_month=now.strftime('%B %Y'),
                         year=year,
                         month=month,
                         statistics=statistics,
                         students=students_today,
                         total_students=len(students_today))

@app.route('/admin/student/<int:student_id>')
def admin_student_detail(student_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    student = Student.query.get_or_404(student_id)
    attendances = Attendance.query.filter_by(student_id=student_id).order_by(Attendance.date.desc()).all()
    return render_template('admin/student_detail.html', student=student, attendances=attendances)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/attendance/<date>')
def admin_get_day_attendance(date):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Query all attendances for the given date with student information
        attendances = db.session.query(
            Attendance,
            Student
        ).join(Student).filter(
            Attendance.date == date_obj
        ).all()
        
        # Format the response
        attendance_data = []
        for att, student in attendances:
            attendance_data.append({
                'student_id': student.id,
                'student_name': student.name,
                'status': att.status or 'Belum Absen',
                'time_in': att.time_in.strftime('%H:%M') if att.time_in else '-',
                'activity': att.activity or '-',
                'photo_path': att.photo_path if att.photo_path else None
            })
        
        return jsonify(attendance_data)
    except Exception as e:
        app.logger.error(f"Error fetching attendance data: {str(e)}")
        return jsonify([])  # Return empty array instead of error

@app.route('/api/attendance/<int:year>/<int:month>/<int:day>')
def get_detailed_attendance(year, month, day):  # Renamed from get_day_attendance
    try:
        # Convert to datetime
        selected_date = datetime(year, month, day).date()
        
        # Query all attendance records for the selected date
        attendances = Attendance.query.filter(
            db.func.date(Attendance.date) == selected_date
        ).join(Student).all()
        
        # Format the attendance data
        attendance_data = []
        for attendance in attendances:
            attendance_data.append({
                'id': attendance.id,
                'student_name': attendance.student.name,
                'status': attendance.attendance_type,
                'time_in': attendance.time_in.strftime('%H:%M') if attendance.time_in else None,
                'activity': attendance.activity,
                'photo_path': attendance.photo_path if attendance.photo_path else None
            })
        
        return jsonify(attendance_data)
    except Exception as e:
        app.logger.error(f"Error fetching attendance data: {str(e)}")
        return jsonify({'error': 'Failed to fetch attendance data'}), 500

# Test endpoint to check student data
@app.route('/test_student/<email>')
def test_student(email):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    student = Student.query.filter_by(email=email).first()
    if student:
        return jsonify({
            'id': student.id,
            'name': student.name,
            'email': student.email,
            'password_length': len(student.password) if student.password else 0
        })
    return jsonify({'error': 'Student not found'}), 404

# Function to ensure attendance data is properly saved
def save_attendance_summary(date):
    # Check if summary exists
    summary = AttendanceSummary.query.filter_by(date=date).first()
    if not summary:
        # Get attendance counts for the date
        attendance_counts = db.session.query(
            db.func.sum(db.case((Attendance.status == 'hadir', 1), else_=0)).label('present'),
            db.func.sum(db.case((Attendance.status == 'sakit', 1), else_=0)).label('sick'),
            db.func.sum(db.case((Attendance.status == 'izin', 1), else_=0)).label('excused')
        ).filter(Attendance.date == date).first()

        # Create new summary
        summary = AttendanceSummary(
            date=date,
            present_count=attendance_counts.present or 0,
            sick_count=attendance_counts.sick or 0,
            excused_count=attendance_counts.excused or 0
        )
        db.session.add(summary)
        db.session.commit()
        logger.info(f"Created attendance summary for date: {date}")

# Automatically save summary when recording attendance
@app.after_request
def after_request(response):
    if request.endpoint == 'attendance' and request.method == 'POST':
        today = datetime.now().date()
        save_attendance_summary(today)
    return response

# Add this function to reset daily attendance counts
def reset_daily_attendance_counts():
    try:
        with app.app_context():
            # Reset all students' daily attendance counts
            students = Student.query.all()
            for student in students:
                student.attendance_count = {
                    'present': 0,
                    'late': 0
                }
            db.session.commit()
            logging.info("Daily attendance counts have been reset")
    except Exception as e:
        logging.error(f"Error resetting attendance counts: {str(e)}")

# Add this to your main section
# if __name__ == '__main__':
#     # Schedule the daily reset at midnight
#     schedule.every().day.at("00:00").do(reset_daily_attendance_counts)
#     
#     # Run the scheduler in a separate thread
#     import threading
#     def run_scheduler():
#         while True:
#             schedule.run_pending()
#             time.sleep(60)
#     
#     scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
#     scheduler_thread.start()
#     
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True, host='0.0.0.0', port=5000)

@app.route('/api/attendance-stats')
def attendance_stats():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401

    # Get monthly attendance statistics
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    # Query for monthly attendance
    monthly_attendance = db.session.query(
        Student.name,
        db.func.count(Attendance.id).label('attendance_count'),
        db.func.sum(case([(Attendance.status == 'Terlambat', 1)], else_=0)).label('late_count')
    ).join(Attendance).filter(
        db.extract('month', Attendance.date) == current_month,
        db.extract('year', Attendance.date) == current_year
    ).group_by(Student.id, Student.name).all()

    # Get attendance statistics for all students
    all_students = Student.query.all()
    total_days = db.session.query(db.func.count(db.distinct(Attendance.date))).scalar() or 1
    
    student_stats = []
    for student in all_students:
        # Count total attendances
        attendance_count = db.session.query(Attendance).filter(
            Attendance.student_id == student.id,
            db.extract('month', Attendance.date) == current_month,
            db.extract('year', Attendance.date) == current_year
        ).count()
        
        # Calculate absent rate
        absent_days = total_days - attendance_count
        
        student_stats.append({
            'name': student.name,
            'attendance_count': attendance_count,
            'absent_days': absent_days
        })
    
    # Sort for most present and most absent students
    most_present = sorted(student_stats, key=lambda x: x['attendance_count'], reverse=True)[:5]
    most_absent = sorted(student_stats, key=lambda x: x['absent_days'], reverse=True)[:5]

    # Get weekly attendance data
    weekly_data = db.session.query(
        db.func.date(Attendance.date).label('date'),
        db.func.count(case([(Attendance.status == 'Hadir', 1)], else_=0)).label('present_count'),
        db.func.count(case([(Attendance.status == 'Terlambat', 1)], else_=0)).label('late_count')
    ).filter(
        Attendance.date >= datetime.now() - timedelta(days=7)
    ).group_by(db.func.date(Attendance.date)).all()

    weekly_stats = {
        'labels': [],
        'present': [],
        'late': []
    }

    for day in weekly_data:
        weekly_stats['labels'].append(day.date.strftime('%Y-%m-%d'))
        weekly_stats['present'].append(day.present_count)
        weekly_stats['late'].append(day.late_count)

    return jsonify({
        'weekly_stats': weekly_stats,
        'most_present': most_present,
        'most_absent': most_absent
    })

@app.route('/api/admin/attendance-stats')
def admin_attendance_stats():
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401

    # Get monthly attendance statistics
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    # Calculate overall statistics
    total_students = Student.query.count()
    total_days = db.session.query(db.func.count(db.distinct(Attendance.date))).scalar() or 1
    
    # Get daily attendance counts for the last 30 days
    daily_stats = db.session.query(
        db.func.date(Attendance.date).label('date'),
        db.func.count(Attendance.id).label('total_present'),
        db.func.count(case([(Attendance.status == 'Terlambat', 1)], else_=0)).label('total_late')
    ).filter(
        Attendance.date >= datetime.now() - timedelta(days=30)
    ).group_by(db.func.date(Attendance.date)).all()

    # Get student attendance statistics
    student_stats = db.session.query(
        Student.name,
        Student.email,
        db.func.count(Attendance.id).label('attendance_count')
    ).outerjoin(Attendance).group_by(Student.id).all()

    # Calculate attendance rates and prepare statistics
    attendance_stats = []
    for stat in student_stats:
        attendance_rate = (stat.attendance_count / total_days) * 100
        attendance_stats.append({
            'name': stat.name,
            'email': stat.email,
            'attendance_rate': round(attendance_rate, 2),
            'present_days': stat.attendance_count,
            'absent_days': total_days - stat.attendance_count
        })

    # Sort by attendance rate
    most_present = sorted(attendance_stats, key=lambda x: x['attendance_rate'], reverse=True)[:5]
    most_absent = sorted(attendance_stats, key=lambda x: x['absent_days'], reverse=True)[:5]

    # Prepare daily statistics for the chart
    daily_data = {
        'labels': [],
        'present': [],
        'absent': []
    }

    for day in daily_stats:
        daily_data['labels'].append(day.date.strftime('%Y-%m-%d'))
        daily_data['present'].append(day.total_present)
        daily_data['absent'].append(total_students - day.total_present)

    return jsonify({
        'overall_stats': {
            'total_students': total_students,
            'total_days': total_days,
            'average_attendance_rate': round(sum(s['attendance_rate'] for s in attendance_stats) / len(attendance_stats), 2)
        },
        'daily_stats': daily_data,
        'most_present': most_present,
        'most_absent': most_absent
    })