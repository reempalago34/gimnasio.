import os
from dotenv import load_dotenv

# Cargar variables desde .env solo en desarrollo local
if os.environ.get('FLASK_ENV') == 'development':
    load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Si existe DATABASE_URL la usa (Coolify/Docker), si no usa SQLite local
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'flaskdb.sqlite')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-default-12345')
    
    # Credenciales de Administrador (Semilla)
    ADMIN_NAME = os.environ.get('ADMIN_NAME', 'Admin')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')