from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models.users import User

bp = Blueprint('auth', __name__)

@bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nameUser = request.form['nameUser']
        passwordUser = request.form['passwordUser']
        
        user = User.query.filter_by(nombre=nameUser).first()
        if user and user.check_password(passwordUser):
            login_user(user)
            return redirect(url_for('auth.dashboard'))
        
        flash('Invalid credentials. Please try again.', 'danger')
    
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    return render_template("login.html")

@bp.route('/dashboard')
@login_required
def dashboard():    
    from app.models.cliente import Cliente
    from app.models.plan import Plan
    from app.models.inscripcion import Inscripcion
    
    from app.models.horario import Horario
    
    total_clientes = Cliente.query.count()
    total_planes = Plan.query.count()
    total_inscripciones = Inscripcion.query.count()
    activas = Inscripcion.query.order_by(Inscripcion.fecha.desc()).limit(10).all()
    
    # Horarios específicos según rol
    mis_horarios = []
    if current_user.rol == 'entrenador':
        mis_horarios = Horario.query.filter_by(idUser=current_user.idUser).all()
    elif current_user.rol in ['usuario', 'admin', 'recepcionista']:
        mis_horarios = current_user.horarios_seleccionados
    
    # Asistencia activa del cliente
    asistencia_cliente = None
    if current_user.rol in ['usuario', 'admin', 'recepcionista']:
        from app.models.asistencia_cliente import AsistenciaCliente
        from datetime import datetime
        asistencia_cliente = AsistenciaCliente.query.filter_by(
            idUser=current_user.idUser,
            hora_salida=None
        ).first()

    return render_template('dashboard.html', 
                           total_clientes=total_clientes, 
                           total_planes=total_planes,
                           total_inscripciones=total_inscripciones,
                           inscripciones=activas,
                           mis_horarios=mis_horarios,
                           asistencia_cliente=asistencia_cliente)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
