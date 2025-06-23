import sys
import os

# Tambahkan folder tempat app.py berada ke sys.path
project_home = '/home/numbers1111111/absensitmd/hybrid-web-app/src'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Opsional: Set environment ke production
os.environ['FLASK_ENV'] = 'production'

# Import aplikasi Flask
from app import app as application
