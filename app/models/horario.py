from app import db

user_horarios = db.Table('user_horarios',
    db.Column('user_id', db.Integer, db.ForeignKey('users.idUser'), primary_key=True),
    db.Column('horario_id', db.Integer, db.ForeignKey('horarios.idHorario'), primary_key=True)
)

class Horario(db.Model):
    __tablename__ = 'horarios'
    idHorario = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, db.ForeignKey('users.idUser'), nullable=False)
    dia_semana = db.Column(db.String(20), nullable=False)
    hora_inicio = db.Column(db.String(10), nullable=False)
    hora_fin = db.Column(db.String(10), nullable=False)
    
    trainer = db.relationship('User', foreign_keys=[idUser], backref=db.backref('horarios_asignados', lazy=True, cascade="all, delete-orphan"))
    usuarios_inscritos = db.relationship('User', secondary=user_horarios, backref=db.backref('horarios_seleccionados', lazy=True))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
