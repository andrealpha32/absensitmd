from app import app, db, reset_daily_attendance_counts
import schedule
import threading
import time
import socket

def find_available_port(start_port, max_port=65535):
    for port in range(start_port, max_port + 1):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('0.0.0.0', port))
            s.close()
            return port
        except OSError:
            continue
    return None

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
    
    # Find available port starting from 5000
    port = find_available_port(5000)
    if port is None:
        print("No available ports found!")
        exit(1)
    
    print(f"Starting server on port {port}")
    
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=port)
