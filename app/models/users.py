from flask_login import UserMixin
from app import db
from app.utils import get_colombia_time
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    idUser = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column('passwordUser', db.String(255), nullable=False)
    rol = db.Column(db.String(20), default='usuario', nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    creado_en = db.Column(db.DateTime, default=get_colombia_time)

    def get_id(self):
        return str(self.idUser)

    @property
    def passwordUser(self):
        raise AttributeError('password is not a readable attribute')

    @passwordUser.setter
    def passwordUser(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def nameUser(self):
        return self.nombre

    @nameUser.setter
    def nameUser(self, value):
        self.nombre = value

    @property
    def emailUser(self):
        return self.email

    @emailUser.setter
    def emailUser(self, value):
        self.email = value

    @property
    def creado_enUser(self):
        return self.creado_en

    def to_dict(self):
        return {
            "idUser": self.idUser,
            "nombre": self.nombre,
            "email": self.email,
            "telefono": self.telefono,
            "rol": self.rol,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()

