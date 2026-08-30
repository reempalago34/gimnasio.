import os
from dotenv import load_dotenv

# Cargar variables desde .env solo en desarrollo local
if os.environ.get('FLASK_ENV') == 'development':
    load_dotenv()

# Subir un nivel para llegar a la raíz del proyecto desde la carpeta config/
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

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

    # Configuración de correo (recuperación de contraseña)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)