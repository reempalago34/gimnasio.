from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models.cliente import Cliente
from app.models.asistencia_cliente import AsistenciaCliente
from app import db
from datetime import datetime
from app.utils import get_colombia_time
from flask_login import current_user

bp = Blueprint('cliente_routes', __name__, url_prefix='/clientes')

@bp.route('/')
@login_required
def index():
    from flask_login import current_user
    if current_user.rol not in ['admin', 'recepcionista']:
        flash('No tienes permisos para ver clientes.', 'danger')
        return redirect(url_for('auth.dashboard'))
    clientes = Cliente.query.all()
    return render_template('clientes/index.html', clientes=clientes)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    from flask_login import current_user
    if request.method == 'POST':
        if current_user.rol == 'usuario':
            nombre = current_user.nombre
        else:
            nombre = request.form['nombre']
            
        edad = request.form['edad']
        telefono = request.form['telefono']
        
        nuevo_cliente = Cliente(nombre=nombre, edad=edad, telefono=telefono)
        nuevo_cliente.save()
        flash('Cliente registrado con éxito', 'success')
        return redirect(url_for('cliente_routes.index'))
        
    return render_template('clientes/add.html')

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    from flask_login import current_user
    if current_user.rol not in ['admin', 'entrenador', 'recepcionista']:
        flash('No tienes permisos para editar clientes.', 'danger')
        return redirect(url_for('cliente_routes.index'))
    cliente = Cliente.query.get_or_404(id)
    if request.method == 'POST':
        cliente.nombre = request.form['nombre']
        cliente.edad = request.form['edad']
        cliente.telefono = request.form['telefono']
        db.session.commit()
        flash('Cliente actualizado con éxito', 'success')
        return redirect(url_for('cliente_routes.index'))
        
    return render_template('clientes/edit.html', cliente=cliente)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    from flask_login import current_user
    if current_user.rol not in ['admin', 'entrenador', 'recepcionista']:
        flash('No tienes permisos para borrar clientes.', 'danger')
        return redirect(url_for('cliente_routes.index'))
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente eliminado con éxito', 'success')
    return redirect(url_for('cliente_routes.index'))

@bp.route('/asistencia/marcar-entrada')
@login_required
def marcar_entrada():
    # Verificar si ya tiene una asistencia activa hoy
    hoy = get_colombia_time().date()
    asistencia_existente = AsistenciaCliente.query.filter_by(
        idUser=current_user.idUser, 
        fecha=hoy,
        hora_salida=None
    ).first()
    
    if asistencia_existente:
        flash('Ya has marcado entrada hoy.', 'warning')
        return redirect(url_for('auth.dashboard'))
    
    nueva_asistencia = AsistenciaCliente(
        idUser=current_user.idUser,
        fecha=hoy,
        hora_entrada=get_colombia_time()
    )
    
    try:
        nueva_asistencia.save()
        flash('¡Bienvenido! Tu entrada ha sido registrada.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar entrada: {str(e)}', 'danger')
        
    return redirect(url_for('auth.dashboard'))

@bp.route('/asistencia/marcar-salida/<int:id_asistencia>')
@login_required
def marcar_salida(id_asistencia):
    asistencia = AsistenciaCliente.query.get_or_404(id_asistencia)
    
    if asistencia.idUser != current_user.idUser:
        flash('No puedes marcar la salida de otro usuario.', 'danger')
        return redirect(url_for('auth.dashboard'))
    
    asistencia.hora_salida = get_colombia_time()
    
    try:
        asistencia.update()
        flash('¡Hasta pronto! Tu salida ha sido registrada.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar salida: {str(e)}', 'danger')
        
    return redirect(url_for('auth.dashboard'))

@bp.route('/asistencia/historial')
@login_required
def historial():
    if current_user.rol in ['admin', 'recepcionista']:
        asistencias = AsistenciaCliente.query.order_by(AsistenciaCliente.fecha.desc(), AsistenciaCliente.hora_entrada.desc()).all()
    else:
        asistencias = AsistenciaCliente.query.filter_by(idUser=current_user.idUser).order_by(AsistenciaCliente.fecha.desc(), AsistenciaCliente.hora_entrada.desc()).all()
        
    return render_template('clientes/historial_asistencia.html', asistencias=asistencias)
