from app import db

class Plan(db.Model):
    __tablename__ = 'planes'
    idPlan = db.Column(db.Integer, primary_key=True)
    nombrePlan = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    duracionMeses = db.Column(db.Integer, nullable=False)

    inscripciones = db.relationship('Inscripcion', back_populates='plan', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "idPlan": self.idPlan,
            "nombrePlan": self.nombrePlan,
            "precio": self.precio,
            "duracionMeses": self.duracionMeses
        }

    def save(self):
        db.session.add(self)
        db.session.commit()
