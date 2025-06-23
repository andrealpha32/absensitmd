from app import app, db, reset_daily_attendance_counts
import schedule
import threading
import time

if __name__ == '__main__':
    # Schedule the daily reset at midnight
    schedule.every().day.at("00:00").do(reset_daily_attendance_counts)
    
    # Run the scheduler in a separate thread
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
