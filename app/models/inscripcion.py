from app import db
from app.utils import get_colombia_time

class Inscripcion(db.Model):
    __tablename__ = 'inscripciones'
    idInscripcion = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=get_colombia_time)
    
    idCliente = db.Column(db.Integer, db.ForeignKey('clientes.idCliente'), nullable=False)
    idPlan = db.Column(db.Integer, db.ForeignKey('planes.idPlan'), nullable=False)

    cliente = db.relationship('Cliente', back_populates='inscripciones')
    plan = db.relationship('Plan', back_populates='inscripciones')

    def to_dict(self):
        return {
            "idInscripcion": self.idInscripcion,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "idCliente": self.idCliente,
            "idPlan": self.idPlan
        }

    def save(self):
        db.session.add(self)
        db.session.commit()
