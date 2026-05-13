from app import db
from app.utils import get_colombia_time

class AsistenciaCliente(db.Model):
    __tablename__ = 'asistencias_clientes'
    idAsistencia = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, db.ForeignKey('users.idUser'), nullable=False)
    fecha = db.Column(db.Date, default=lambda: get_colombia_time().date(), nullable=False)
    hora_entrada = db.Column(db.DateTime, default=get_colombia_time, nullable=False)
    hora_salida = db.Column(db.DateTime, nullable=True)
    observaciones = db.Column(db.Text, nullable=True)

    # Relación
    usuario = db.relationship('User', backref=db.backref('asistencias_gym', lazy=True))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()
