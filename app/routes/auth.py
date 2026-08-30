from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from app.models.users import User
from app import db
from app.utils import send_email

bp = Blueprint('auth', __name__)

RESET_TOKEN_MAX_AGE = 3600  # 1 hora
RESET_SALT = 'password-reset'

def _get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

def generar_token_reset(user_email):
    return _get_serializer().dumps(user_email, salt=RESET_SALT)

def verificar_token_reset(token):
    try:
        return _get_serializer().loads(token, salt=RESET_SALT, max_age=RESET_TOKEN_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None

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

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email).first() if email else None

        if user:
            token = generar_token_reset(user.email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            cuerpo_html = f"""
                <p>Hola {user.nombre},</p>
                <p>Recibimos una solicitud para restablecer tu contraseña en Fit Nation.</p>
                <p><a href="{reset_url}">Haz clic aquí para crear una nueva contraseña</a></p>
                <p>Este enlace expira en 1 hora. Si no solicitaste esto, ignora este correo.</p>
            """
            try:
                send_email(user.email, 'Recuperación de contraseña - Fit Nation', cuerpo_html)
            except Exception as e:
                print(f"Error al enviar correo de recuperación: {str(e)}")

        # Mismo mensaje exista o no el correo, para no revelar qué correos están registrados
        flash('Si el correo está registrado, te enviamos un enlace para restablecer tu contraseña.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')

@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    email = verificar_token_reset(token)
    if not email:
        flash('El enlace de recuperación no es válido o expiró. Solicita uno nuevo.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('El enlace de recuperación no es válido.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirmPassword', '')

        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'danger')
            return render_template('reset_password.html', token=token)

        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('reset_password.html', token=token)

        user.passwordUser = password
        db.session.commit()
        flash('Tu contraseña fue actualizada. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=token)
