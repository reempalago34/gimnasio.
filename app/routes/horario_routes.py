from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.horario import Horario
from app.models.users import User
from app.models.asistencia import AsistenciaEntrenador
from app import db
from datetime import datetime
from app.utils import get_colombia_time

bp = Blueprint('horario_routes', __name__, url_prefix='/horarios')

@bp.route('/')
@login_required
def index():
    # Todos pueden ver los horarios ahora
    if current_user.rol == 'entrenador':
        horarios = Horario.query.filter_by(idUser=current_user.idUser).all()
    else:
        horarios = Horario.query.all()
        
    # Buscar asistencias activas para el entrenador actual
    asistencia_activa = None
    if current_user.rol == 'entrenador':
        asistencia_activa = AsistenciaEntrenador.query.filter_by(
            idUser=current_user.idUser, 
            hora_salida=None
        ).first()
        
    return render_template('horarios/index.html', horarios=horarios, asistencia_activa=asistencia_activa)


@bp.route('/asistencia/marcar-entrada/<int:id_horario>')
@login_required
def marcar_entrada(id_horario):
    if current_user.rol != 'entrenador':
        flash('Solo los entrenadores pueden marcar asistencia.', 'danger')
        return redirect(url_for('horario_routes.index'))
    
    # Verificar si ya tiene una asistencia activa hoy para este horario
    hoy = get_colombia_time().date()
    asistencia_existente = AsistenciaEntrenador.query.filter_by(
        idHorario=id_horario, 
        idUser=current_user.idUser, 
        fecha=hoy,
        hora_salida=None
    ).first()
    
    if asistencia_existente:
        flash('Ya has marcado entrada para este horario hoy.', 'warning')
        return redirect(url_for('horario_routes.index'))
    
    nueva_asistencia = AsistenciaEntrenador(
        idHorario=id_horario,
        idUser=current_user.idUser,
        fecha=hoy,
        hora_entrada=get_colombia_time()
    )
    
    try:
        nueva_asistencia.save()
        flash('Entrada registrada con éxito. ¡Buen entrenamiento!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar entrada: {str(e)}', 'danger')
        
    return redirect(url_for('horario_routes.index'))

@bp.route('/asistencia/marcar-salida/<int:id_asistencia>')
@login_required
def marcar_salida(id_asistencia):
    asistencia = AsistenciaEntrenador.query.get_or_404(id_asistencia)
    
    if asistencia.idUser != current_user.idUser:
        flash('No puedes marcar la salida de otro entrenador.', 'danger')
        return redirect(url_for('horario_routes.index'))
    
    asistencia.hora_salida = get_colombia_time()
    
    try:
        asistencia.update()
        flash('Salida registrada con éxito. ¡Buen descanso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar salida: {str(e)}', 'danger')
        
    return redirect(url_for('horario_routes.index'))

@bp.route('/historial')
@login_required
def historial():
    if current_user.rol == 'admin':
        asistencias = AsistenciaEntrenador.query.order_by(AsistenciaEntrenador.fecha.desc(), AsistenciaEntrenador.hora_entrada.desc()).all()
    elif current_user.rol == 'entrenador':
        asistencias = AsistenciaEntrenador.query.filter_by(idUser=current_user.idUser).order_by(AsistenciaEntrenador.fecha.desc(), AsistenciaEntrenador.hora_entrada.desc()).all()
    else:
        flash('No tienes permisos para ver el historial.', 'danger')
        return redirect(url_for('horario_routes.index'))
        
    return render_template('horarios/historial.html', asistencias=asistencias)

@bp.route('/seleccionar/<int:id>')
@login_required
def seleccionar(id):
    horario = Horario.query.get_or_404(id)
    if current_user not in horario.usuarios_inscritos:
        horario.usuarios_inscritos.append(current_user)
        db.session.commit()
        flash(f'Has seleccionado el horario: {horario.dia_semana} {horario.hora_inicio}-{horario.hora_fin}', 'success')
    else:
        flash('Ya tienes seleccionado este horario.', 'info')
    return redirect(url_for('horario_routes.index'))

@bp.route('/deseleccionar/<int:id>')
@login_required
def deseleccionar(id):
    horario = Horario.query.get_or_404(id)
    if current_user in horario.usuarios_inscritos:
        horario.usuarios_inscritos.remove(current_user)
        db.session.commit()
        flash('Horario removido de tu lista.', 'info')
    return redirect(url_for('horario_routes.index'))

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if current_user.rol != 'admin':
        flash('Solo el administrador puede asignar horarios.', 'danger')
        return redirect(url_for('horario_routes.index'))
    
    trainers = User.query.filter_by(rol='entrenador').all()
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    if request.method == 'POST':
        idUser = request.form.get('idUser')
        dia_semana = request.form.get('dia_semana')
        hora_inicio = request.form.get('hora_inicio')
        hora_fin = request.form.get('hora_fin')
        
        nuevo_horario = Horario(idUser=idUser, dia_semana=dia_semana, hora_inicio=hora_inicio, hora_fin=hora_fin)
        try:
            nuevo_horario.save()
            flash('Horario asignado con éxito.', 'success')
            return redirect(url_for('horario_routes.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al asignar horario: {str(e)}', 'danger')
        
    return render_template('horarios/add.html', trainers=trainers, dias=dias)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if current_user.rol != 'admin':
        flash('Solo el administrador puede editar horarios.', 'danger')
        return redirect(url_for('horario_routes.index'))
    
    horario = Horario.query.get_or_404(id)
    trainers = User.query.filter_by(rol='entrenador').all()
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    if request.method == 'POST':
        horario.idUser = request.form.get('idUser')
        horario.dia_semana = request.form.get('dia_semana')
        horario.hora_inicio = request.form.get('hora_inicio')
        horario.hora_fin = request.form.get('hora_fin')
        
        try:
            db.session.commit()
            flash('Horario actualizado con éxito.', 'success')
            return redirect(url_for('horario_routes.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}', 'danger')
            
    return render_template('horarios/edit.html', horario=horario, trainers=trainers, dias=dias)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    if current_user.rol != 'admin':
        flash('No tienes permisos para borrar horarios.', 'danger')
        return redirect(url_for('horario_routes.index'))
        
    horario = Horario.query.get_or_404(id)
    try:
        horario.delete()
        flash('Horario eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}', 'danger')
        
    return redirect(url_for('horario_routes.index'))
