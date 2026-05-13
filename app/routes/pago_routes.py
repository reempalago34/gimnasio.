from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.pago import Pago
from app.models.cliente import Cliente
from app import db

bp = Blueprint('pago_routes', __name__, url_prefix='/pagos')

@bp.route('/')
@login_required
def index():
    if current_user.rol in ['admin', 'recepcionista']:
        # Admin y recepcionista ven todos los pagos
        pagos = Pago.query.order_by(Pago.fecha.desc()).all()
    elif current_user.rol == 'usuario':
        # El usuario solo ve sus propios pagos
        # Buscamos el cliente que corresponda al usuario actual (por nombre como enlace simple)
        cliente = Cliente.query.filter_by(nombre=current_user.nombre).first()
        if cliente:
            pagos = Pago.query.filter_by(idCliente=cliente.idCliente).order_by(Pago.fecha.desc()).all()
        else:
            pagos = []
    else:
        # Entrenadores y otros no tienen acceso
        flash('No tienes permisos para ver el historial de pagos.', 'danger')
        return redirect(url_for('auth.dashboard'))
        
    return render_template('pagos/index.html', pagos=pagos)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if current_user.rol not in ['admin', 'recepcionista']:
        flash('Solo admin o recepcionista pueden registrar pagos.', 'danger')
        return redirect(url_for('pago_routes.index'))
    
    clientes = Cliente.query.all()
    if request.method == 'POST':
        idCliente = request.form.get('idCliente')
        monto = request.form.get('monto')
        metodo = request.form.get('metodo_pago')
        
        nuevo_pago = Pago(idCliente=idCliente, monto=monto, metodo_pago=metodo)
        try:
            nuevo_pago.save()
            flash('Pago registrado con éxito.', 'success')
            return redirect(url_for('pago_routes.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar pago: {str(e)}', 'danger')
            
    return render_template('pagos/add.html', clientes=clientes)
