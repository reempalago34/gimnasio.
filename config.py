import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///flaskdb.sqlite')
    if database_url.startswith('sqlite:///'):
        # For SQLite, if it's a relative path, make it absolute relative to basedir
        db_path = database_url.replace('sqlite:///', '')
        if not os.path.isabs(db_path):
            database_url = 'sqlite:///' + os.path.join(basedir, db_path)
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production-12345')
    
    # Admin Seed Credentials
    ADMIN_NAME = os.environ.get('ADMIN_NAME', 'Admin')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')