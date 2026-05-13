from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_file, flash
from flask_login import login_required, current_user, login_user
from app.models.users import User
from app import db
from io import BytesIO
import base64
import json

bp = Blueprint('user', __name__, url_prefix='/User')


@bp.route('/')
def index():
    data = User.query.all()
    return render_template('users/index.html', data=data)

@bp.route('/js')
def indexjs():
    data = User.query.all()
        # Serializar los datos usando una comprensión de lista
    result = [user.to_dict() for user in data]  # Asegúrate de que el modelo User tenga un método to_dict()
    
    # Devolver la respuesta JSON
    return jsonify(result)

@bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        nameUser = request.form.get('nameUser')
        telefonoUser = request.form.get('telefonoUser')
        emailUser = request.form.get('emailUser')
        password = request.form.get('passwordUser')
        confirmPassword = request.form.get('confirmPassword')

        # Validar campos obligatorios
        if not nameUser or not password or not confirmPassword:
            flash('Todos los campos son obligatorios.', 'danger')
            return render_template('users/add.html')

        # Validar que las contraseñas coincidan
        if password != confirmPassword:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('users/add.html')

        # Validar longitud de contraseña
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'danger')
            return render_template('users/add.html')

        existing_user = User.query.filter_by(nombre=nameUser).first()
        if existing_user:
            flash('El nombre de usuario ya está en uso.', 'warning')
            return render_template('users/add.html')

        if emailUser:
            existing_email = User.query.filter_by(email=emailUser).first()
            if existing_email:
                flash('El correo electrónico ya está registrado.', 'warning')
                return render_template('users/add.html')

        new_user = User(nombre=nameUser, telefono=telefonoUser, email=emailUser, passwordUser=password)
        
        try:
            if current_user.is_authenticated and current_user.rol == 'admin':
                new_user.rol = request.form.get('rol', 'usuario')
                db.session.add(new_user)
                db.session.commit()
                flash('Usuario creado correctamente por el administrador.', 'success')
                return redirect(url_for('user.index'))
            else:
                db.session.add(new_user)
                db.session.commit()
                # Autenticar al usuario automáticamente después de crear la cuenta
                login_user(new_user)
                flash('¡Cuenta creada correctamente! Bienvenido.', 'success')
                return redirect(url_for('auth.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la cuenta: {str(e)}', 'danger')
            return render_template('users/add.html')

    return render_template('users/add.html')

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    user = User.query.get_or_404(id)
    if current_user.idUser != user.idUser and current_user.rol != 'admin':
        flash('No puedes editar otro usuario.', 'danger')
        return redirect(url_for('user.index'))
    if request.method == 'POST':
        nameUser = request.form.get('nameUser')
        telefonoUser = request.form.get('telefonoUser')
        emailUser = request.form.get('emailUser')
        password = request.form.get('passwordUser')

        if not nameUser:
            flash('El nombre de usuario es obligatorio.', 'danger')
            return render_template('users/edit.html', user=user)

        duplicate_user = User.query.filter(User.nombre == nameUser, User.idUser != user.idUser).first()
        if duplicate_user:
            flash('El nombre de usuario ya está en uso.', 'warning')
            return render_template('users/edit.html', user=user)

        if emailUser:
            duplicate_email = User.query.filter(User.email == emailUser, User.idUser != user.idUser).first()
            if duplicate_email:
                flash('El correo electrónico ya está registrado.', 'warning')
                return render_template('users/edit.html', user=user)

        user.nameUser = nameUser
        user.telefono = telefonoUser
        user.emailUser = emailUser
        if password:
            confirmPassword = request.form.get('confirmPassword')
            if password != confirmPassword:
                 flash('Las contraseñas no coinciden.', 'danger')
                 return render_template('users/edit.html', user=user)
            if len(password) < 6:
                 flash('La contraseña debe tener al menos 6 caracteres.', 'danger')
                 return render_template('users/edit.html', user=user)

            user.passwordUser = password

        if current_user.rol == 'admin':
            rol = request.form.get('rol')
            if rol in ['admin', 'usuario', 'entrenador', 'recepcionista']:
                user.rol = rol

        try:
            db.session.commit()
            flash('Usuario actualizado correctamente.', 'success')
            return redirect(url_for('user.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el usuario: {str(e)}', 'danger')
            return render_template('users/edit.html', user=user)

    return render_template('users/edit.html', user=user)
@bp.route('/detail/<int:id>')
def detail(id):
    user = User.query.get_or_404(id)
    return render_template('users/detail.html', user=user)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    user = User.query.get_or_404(id)
    if current_user.idUser != user.idUser and current_user.rol != 'admin':
        flash('No tienes permisos para eliminar este usuario.', 'danger')
        return redirect(url_for('user.index'))
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Usuario eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el usuario: {str(e)}', 'danger')
    return redirect(url_for('user.index'))
