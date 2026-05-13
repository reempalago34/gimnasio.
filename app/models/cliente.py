from app import db

class Cliente(db.Model):
    __tablename__ = 'clientes'
    idCliente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)

    inscripciones = db.relationship('Inscripcion', back_populates='cliente', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "idCliente": self.idCliente,
            "nombre": self.nombre,
            "edad": self.edad,
            "telefono": self.telefono,
            "email": self.email
        }

    def save(self):
        db.session.add(self)
        db.session.commit()
