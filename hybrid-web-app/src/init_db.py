from app import app, db
from models import Admin, Student, Attendance
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    try:
        with app.app_context():
            logger.info("Dropping all tables...")
            db.drop_all()
            
            logger.info("Creating all tables...")
            db.create_all()
            
            # Create admin
            logger.info("Creating admin account...")
            admin = Admin(
                username='admin',
                password='admin123',
                email='admin@example.com'
            )
            
            db.session.add(admin)
            db.session.commit()
            
            # Verify admin was created
            created_admin = Admin.query.filter_by(username='admin').first()
            if created_admin:
                logger.info("=== Admin Account Created Successfully ===")
                logger.info(f"Username: {created_admin.username}")
                logger.info(f"Password: {created_admin.password}")
                logger.info(f"Email: {created_admin.email}")
            else:
                logger.error("Failed to create admin account!")
                
    except Exception as e:
        logger.error(f"Error during database initialization: {str(e)}")
        db.session.rollback()
        raise

if __name__ == '__main__':
    init_db()
