from app import db
from app.utils import get_colombia_time

class AsistenciaEntrenador(db.Model):
    __tablename__ = 'asistencias_entrenadores'
    idAsistencia = db.Column(db.Integer, primary_key=True)
    idHorario = db.Column(db.Integer, db.ForeignKey('horarios.idHorario'), nullable=False)
    idUser = db.Column(db.Integer, db.ForeignKey('users.idUser'), nullable=False)
    fecha = db.Column(db.Date, default=lambda: get_colombia_time().date(), nullable=False)
    hora_entrada = db.Column(db.DateTime, default=get_colombia_time, nullable=False)
    hora_salida = db.Column(db.DateTime, nullable=True)
    observaciones = db.Column(db.Text, nullable=True)

    # Relaciones
    horario = db.relationship('Horario', backref=db.backref('asistencias', lazy=True))
    entrenador = db.relationship('User', backref=db.backref('asistencias_realizadas', lazy=True))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()
