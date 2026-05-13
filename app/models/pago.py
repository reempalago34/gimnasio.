from app import db
from app.utils import get_colombia_time

class Pago(db.Model):
    __tablename__ = 'pagos'
    idPago = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=get_colombia_time)
    metodo_pago = db.Column(db.String(50), default='Efectivo')
    
    idCliente = db.Column(db.Integer, db.ForeignKey('clientes.idCliente'), nullable=False)
    idInscripcion = db.Column(db.Integer, db.ForeignKey('inscripciones.idInscripcion'), nullable=True)

    cliente = db.relationship('Cliente', backref=db.backref('pagos', lazy=True, cascade="all, delete-orphan"))
    inscripcion = db.relationship('Inscripcion', backref=db.backref('pagos', lazy=True))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            "idPago": self.idPago,
            "monto": self.monto,
            "fecha": self.fecha.isoformat(),
            "metodo_pago": self.metodo_pago,
            "cliente": self.cliente.nombre if self.cliente else "N/A"
        }
