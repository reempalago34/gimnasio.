from flask import Blueprint, render_template, request, jsonify, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
import qrcode
import io
import base64
import json
from app.models.cliente import Cliente
from app.models.inscripcion import Inscripcion
from app.models.pago import Pago
from app.models.users import User

bp = Blueprint('qr', __name__)

def verificar_estado_pago(id_cliente):
    """Verifica si el cliente tiene pagos para su inscripción más reciente"""
    inscripcion = Inscripcion.query.filter_by(idCliente=id_cliente).order_by(Inscripcion.fecha.desc()).first()
    if not inscripcion:
        return False, "No tiene inscripciones"
    
    pagos = Pago.query.filter_by(idInscripcion=inscripcion.idInscripcion).all()
    if not pagos:
        return False, "Inscripción sin pagos"
    
    return True, "Pagado"

def verificar_permisos_cliente(id_cliente):
    """Verifica si el usuario actual tiene permisos para acceder al QR del cliente"""
    if current_user.rol == 'usuario':
        cliente = Cliente.query.filter_by(nombre=current_user.nombre).first()
        if not cliente or cliente.idCliente != id_cliente:
            return None, 'No tienes permiso para ver este QR'
    elif current_user.rol in ['admin', 'recepcionista']:
        cliente = Cliente.query.get_or_404(id_cliente)
    else:
        return None, 'No tienes permiso para generar QR'
    
    return cliente, None

def obtener_inscripcion_activa(id_cliente):
    """Obtiene la inscripción más reciente de un cliente"""
    inscripcion = Inscripcion.query.filter_by(idCliente=id_cliente).order_by(Inscripcion.fecha.desc()).first()
    if not inscripcion:
        return None, 'El cliente no tiene inscripciones activas'
    return inscripcion, None

def generar_qr_data(cliente, inscripcion, pagado, mensaje_pago):
    """Crea el diccionario de datos para el QR"""
    return {
        'id_cliente': cliente.idCliente,
        'nombre': cliente.nombre,
        'id_inscripcion': inscripcion.idInscripcion,
        'fecha_inscripcion': inscripcion.fecha.isoformat() if inscripcion.fecha else None,
        'id_plan': inscripcion.idPlan,
        'pagado': pagado,
        'estado_pago': mensaje_pago
    }

def crear_qr_image(qr_data):
    """Genera la imagen del QR a partir de los datos"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(json.dumps(qr_data))
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

@bp.route('/generar_qr/<int:id_cliente>')
@login_required
def generar_qr(id_cliente):
    """Genera un QR para un cliente con su información y estado de pago"""
    # Verificar permisos
    cliente, error_msg = verificar_permisos_cliente(id_cliente)
    if error_msg:
        flash(error_msg, 'danger')
        return redirect(url_for('auth.dashboard'))
    
    # Verificar si tiene inscripción
    inscripcion, error_msg = obtener_inscripcion_activa(id_cliente)
    if error_msg:
        flash(error_msg, 'warning')
        return redirect(url_for('auth.dashboard'))
    
    # Verificar estado de pago
    pagado, mensaje_pago = verificar_estado_pago(id_cliente)
    
    # Crear datos del QR y generar imagen
    qr_data = generar_qr_data(cliente, inscripcion, pagado, mensaje_pago)
    img = crear_qr_image(qr_data)
    
    # Verificar si se solicita como imagen (para preview)
    if request.args.get('format') == 'image':
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
    
    # Convertir a base64 para mostrar en HTML
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode()
    
    return render_template('qr/generar_qr.html', 
                          cliente=cliente, 
                          inscripcion=inscripcion,
                          pagado=pagado,
                          mensaje_pago=mensaje_pago,
                          qr_image=img_base64)

@bp.route('/descargar_qr/<int:id_cliente>')
@login_required
def descargar_qr(id_cliente):
    """Descarga el QR como imagen PNG"""
    # Verificar permisos
    cliente, error_msg = verificar_permisos_cliente(id_cliente)
    if error_msg:
        flash(error_msg, 'danger')
        return redirect(url_for('auth.dashboard'))
    
    # Verificar si tiene inscripción
    inscripcion, error_msg = obtener_inscripcion_activa(id_cliente)
    if error_msg:
        flash(error_msg, 'warning')
        return redirect(url_for('auth.dashboard'))
    
    # Verificar estado de pago
    pagado, mensaje_pago = verificar_estado_pago(id_cliente)
    
    # Crear datos del QR y generar imagen
    qr_data = generar_qr_data(cliente, inscripcion, pagado, mensaje_pago)
    img = crear_qr_image(qr_data)
    
    # Guardar en memoria para descargar
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png', 
                     as_attachment=True, 
                     download_name=f'qr_{cliente.nombre}.png')

@bp.route('/leer_qr', methods=['POST'])
@login_required
def leer_qr():
    """Lee un QR y muestra la información del cliente y estado de pago"""
    data = request.json
    qr_content = data.get('qr_content')
    
    if not qr_content:
        return jsonify({'error': 'No se proporcionó contenido del QR'}), 400
    
    try:
        qr_data = json.loads(qr_content)
        id_cliente = qr_data.get('id_cliente')

        # Solo admin/recepcionista pueden leer QR ajenos; un 'usuario' solo el suyo
        cliente, error_msg = verificar_permisos_cliente(id_cliente)
        if error_msg:
            return jsonify({'error': error_msg}), 403

        inscripcion = Inscripcion.query.get_or_404(qr_data.get('id_inscripcion'))
        if inscripcion.idCliente != cliente.idCliente:
            return jsonify({'error': 'La inscripción no corresponde a este cliente'}), 400

        # Verificar estado de pago actual
        pagado, mensaje_pago = verificar_estado_pago(id_cliente)
        
        return jsonify({
            'success': True,
            'cliente': cliente.to_dict(),
            'inscripcion': inscripcion.to_dict(),
            'pagado': pagado,
            'estado_pago': mensaje_pago
        })
    except Exception as e:
        return jsonify({'error': f'Error al leer QR: {str(e)}'}), 400