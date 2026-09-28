"""Pruebas del blueprint de pagos (/pagos/*)."""


# ------------------------------------------------------------------- index
def test_index_como_admin_ve_todos(admin_client, cliente_factory, pago_factory):
    primero = cliente_factory(nombre='Cliente Pagos')
    segundo = cliente_factory(nombre='Otro Cliente')
    pago_factory(primero, monto=10000.0)
    pago_factory(segundo, monto=20000.0)

    response = admin_client.get('/pagos/')

    assert response.status_code == 200
    assert b'Historial de Pagos' in response.data
    assert b'Cliente Pagos' in response.data
    assert b'Otro Cliente' in response.data
    assert b'10,000.00' in response.data
    assert b'20,000.00' in response.data


def test_index_como_recepcionista(staff_client, cliente_factory, pago_factory):
    cliente = cliente_factory(nombre='Cliente Staff')
    pago_factory(cliente, monto=30000.0)

    response = staff_client.get('/pagos/')

    assert response.status_code == 200
    assert b'Cliente Staff' in response.data
    assert b'30,000.00' in response.data


def test_index_como_entrenador_prohibido(trainer_client):
    response = trainer_client.get('/pagos/', follow_redirects=True)

    assert response.status_code == 200
    assert b'No tienes permisos para ver el historial de pagos.' in response.data


def test_index_como_usuario_solo_ve_los_suyos(
    user_client, normal_user, cliente_factory, pago_factory
):
    mio = cliente_factory(nombre=normal_user.nombre)
    pago_factory(mio, monto=55000.0)
    ajeno = cliente_factory(nombre='Cliente Ajeno')
    pago_factory(ajeno, monto=99999.0)

    response = user_client.get('/pagos/')

    assert response.status_code == 200
    assert b'55,000.00' in response.data
    assert b'Cliente Ajeno' not in response.data
    assert b'99,999.00' not in response.data


def test_index_como_usuario_sin_cliente_listo_vacio(user_client, normal_user):
    # No existe Cliente con el nombre del usuario: lista vacia, sin error
    response = user_client.get('/pagos/')

    assert response.status_code == 200
    assert b'Cliente Ajeno' not in response.data


def test_index_sin_sesion(client):
    response = client.get('/pagos/')

    assert response.status_code == 302
    assert response.headers['Location'].startswith('/?next=')


# --------------------------------------------------------------------- add
def test_add_get_como_admin(admin_client, cliente_factory):
    cliente_factory(nombre='Cliente Para Pago')

    response = admin_client.get('/pagos/add')

    assert response.status_code == 200
    assert b'name="monto"' in response.data
    assert b'Cliente Para Pago' in response.data


def test_add_get_como_entrenador_prohibido(trainer_client):
    response = trainer_client.get('/pagos/add', follow_redirects=True)

    assert response.status_code == 200
    assert b'Solo admin o recepcionista pueden registrar pagos.' in response.data


def test_add_post_como_admin(admin_client, cliente_factory, app):
    from app.models.pago import Pago

    cliente = cliente_factory(nombre='Cliente Cobrado')

    response = admin_client.post('/pagos/add', data={
        'idCliente': str(cliente.idCliente),
        'monto': '75000',
        'metodo_pago': 'Transferencia',
    })

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/pagos/')

    pago = Pago.query.filter_by(idCliente=cliente.idCliente).first()
    assert pago is not None
    assert pago.monto == 75000.0
    assert pago.metodo_pago == 'Transferencia'


def test_add_post_como_recepcionista(staff_client, cliente_factory, app):
    from app.models.pago import Pago

    cliente = cliente_factory(nombre='Cliente Staff Cobra')

    response = staff_client.post('/pagos/add', data={
        'idCliente': str(cliente.idCliente),
        'monto': '50000',
        'metodo_pago': 'Efectivo',
    })

    assert response.status_code == 302
    assert Pago.query.filter_by(idCliente=cliente.idCliente).first() is not None


def test_add_post_como_entrenador_prohibido(trainer_client, cliente_factory, app):
    from app.models.pago import Pago

    cliente = cliente_factory(nombre='Cliente No Cobrado')
    antes = Pago.query.count()

    response = trainer_client.post('/pagos/add', data={
        'idCliente': str(cliente.idCliente),
        'monto': '1',
        'metodo_pago': 'Efectivo',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Solo admin o recepcionista pueden registrar pagos.' in response.data
    assert Pago.query.count() == antes


def test_add_sin_sesion(client, cliente_factory, app):
    from app.models.pago import Pago

    cliente = cliente_factory(nombre='Cliente Anon')
    antes = Pago.query.count()

    response = client.post('/pagos/add', data={
        'idCliente': str(cliente.idCliente),
        'monto': '1',
        'metodo_pago': 'Efectivo',
    })

    assert response.status_code == 302
    assert Pago.query.count() == antes
