# This file contains configuration settings for the application.

import os
from datetime import timedelta

class Config:
    DEBUG = True
    SECRET_KEY = 'dev-secret-key-123'  # Changed to a fixed value for testing
    
    # Define the base directory of the project
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # Set the database path to be in the root directory
    DB_PATH = os.path.join(BASE_DIR, 'instance', 'attendance.db')
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Use absolute path for database
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    # Add other configuration variables as needed