import sys
import os

# Set path ke folder src (di mana app.py dan config.py berada)
project_home = '/home/LebahMadu/absensitmd/hybrid-web-app/src'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment ke production (opsional)
os.environ['FLASK_ENV'] = 'production'

# Import dan jalankan aplikasi Flask
from app import app as application  # 'app' adalah nama file app.py, dan 'app' adalah objek Flask
