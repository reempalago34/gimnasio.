from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.inscripcion import Inscripcion
from app.models.cliente import Cliente
from app.models.plan import Plan
from app import db

bp = Blueprint('inscripcion_routes', __name__, url_prefix='/inscripciones')

@bp.route('/')
@login_required
def index():
    if current_user.rol == 'usuario':
        # Los usuarios normales solo ven sus propias inscripciones
        inscripciones = Inscripcion.query.join(Cliente).filter(Cliente.nombre == current_user.nombre).all()
        has_active_inscription = len(inscripciones) > 0
    elif current_user.rol in ['admin', 'recepcionista']:
        # El personal ve todas las inscripciones
        inscripciones = Inscripcion.query.order_by(Inscripcion.fecha.desc()).all()
        has_active_inscription = False
    else:
        flash('No tienes permisos para ver esta sección.', 'danger')
        return redirect(url_for('auth.dashboard'))
            
    return render_template('inscripciones/index.html', 
                         inscripciones=inscripciones, 
                         has_active_inscription=has_active_inscription)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    from app.models.horario import Horario
    planes = Plan.query.all()
    horarios = Horario.query.all()
    
    # Prevent users from accessing the add page if they already have an inscription
    if current_user.rol == 'usuario':
        user_inscription = Inscripcion.query.join(Cliente).filter(Cliente.nombre == current_user.nombre).first()
        if user_inscription:
            flash('Ya tienes una inscripción activa. Debes cancelarla para cambiar de plan.', 'warning')
            return redirect(url_for('inscripcion_routes.index'))

    if request.method == 'POST':
        if current_user.rol == 'usuario':
            nombre = current_user.nombre
            email = current_user.email
        else:
            nombre = request.form.get('nombre')
            email = request.form.get('email')
            
        edad = request.form.get('edad')
        telefono = request.form.get('telefono')
        idPlan = request.form.get('idPlan')
        idHorario = request.form.get('idHorario')
        terminos = request.form.get('terminos')

        if not terminos:
            flash('Debes aceptar los términos y condiciones antes de registrarte al gimnasio.', 'warning')
            return redirect(url_for('inscripcion_routes.add'))

        cliente = Cliente.query.filter_by(nombre=nombre).first()
        
        if cliente:
            # Check if the client already has an active inscription
            if cliente.inscripciones:
                flash('El usuario ya tiene una inscripción activa. Debe cancelarla para poder inscribirse a un nuevo plan.', 'warning')
                return redirect(url_for('inscripcion_routes.index'))
            
            # Update data if provided
            if edad: cliente.edad = edad
            if telefono: cliente.telefono = telefono
            if email: cliente.email = email
            db.session.commit()
        else:
            cliente = Cliente(nombre=nombre, edad=edad, telefono=telefono, email=email)
            db.session.add(cliente)
            db.session.commit()
            
        # Realizar la inscripción
        nueva_inscripcion = Inscripcion(idCliente=cliente.idCliente, idPlan=idPlan)
        nueva_inscripcion.save()

        # Automatizar el Pago
        from app.models.pago import Pago
        plan_seleccionado = Plan.query.get(idPlan)
        if plan_seleccionado:
            nuevo_pago = Pago(
                idCliente=cliente.idCliente, 
                idInscripcion=nueva_inscripcion.idInscripcion,
                monto=plan_seleccionado.precio,
                metodo_pago='Automático (Inscripción)'
            )
            nuevo_pago.save()

        # Vincular el horario seleccionado al usuario (si se proporcionó)
        if idHorario:
            horario = Horario.query.get(idHorario)
            if horario and current_user not in horario.usuarios_inscritos:
                horario.usuarios_inscritos.append(current_user)
                db.session.commit()

        flash('¡Inscripción, selección de horario y pago completados con éxito!', 'success')
        return redirect(url_for('inscripcion_routes.index'))
        
    return render_template('inscripciones/add.html', planes=planes, horarios=horarios)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    inscripcion = Inscripcion.query.get_or_404(id)
    
    # Check if the user has permission to delete this inscription
    # Only admin, employee, or the owner of the inscription
    is_owner = (current_user.rol == 'usuario' and inscripcion.cliente.nombre == current_user.nombre)
    is_staff = (current_user.rol in ['admin', 'recepcionista'])
    
    if not (is_owner or is_staff):
        flash('No tienes permiso para realizar esta acción.', 'danger')
        return redirect(url_for('inscripcion_routes.index'))

    db.session.delete(inscripcion)
    db.session.commit()
    flash('Inscripción cancelada con éxito.', 'success')
    return redirect(url_for('inscripcion_routes.index'))
