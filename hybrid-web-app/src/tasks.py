from models import db, Attendance, AttendanceSummary
from datetime import datetime, timedelta
import schedule
import time

def process_daily_attendance():
    yesterday = datetime.now().date() - timedelta(days=1)
    
    # Get attendance counts
    attendance_counts = db.session.query(
        Attendance.status,
        db.func.count(Attendance.id)
    ).filter(
        db.cast(Attendance.date, db.Date) == yesterday
    ).group_by(Attendance.status).all()
    
    # Create summary
    summary = AttendanceSummary(
        date=yesterday,
        present_count=next((count for status, count in attendance_counts if status == 'hadir'), 0),
        sick_count=next((count for status, count in attendance_counts if status == 'sakit'), 0),
        excused_count=next((count for status, count in attendance_counts if status == 'izin'), 0)
    )
    
    db.session.add(summary)
    db.session.commit()

def start_scheduler():
    schedule.every().day.at("00:00").do(process_daily_attendance)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    start_scheduler()
