"""Pruebas del blueprint de clientes (/clientes/*), incluida la asistencia."""


# ------------------------------------------------------------------- index
def test_index_como_admin(admin_client, cliente):
    response = admin_client.get('/clientes/')

    assert response.status_code == 200
    assert b'Listado de Clientes' in response.data
    assert cliente.nombre.encode() in response.data


def test_index_como_recepcionista(staff_client, cliente):
    response = staff_client.get('/clientes/')

    assert response.status_code == 200
    assert cliente.nombre.encode() in response.data


def test_index_como_entrenador_prohibido(trainer_client):
    response = trainer_client.get('/clientes/', follow_redirects=True)

    assert response.status_code == 200
    assert b'No tienes permisos para ver clientes.' in response.data


def test_index_como_usuario_prohibido(user_client):
    response = user_client.get('/clientes/', follow_redirects=True)

    assert response.status_code == 200
    assert b'No tienes permisos para ver clientes.' in response.data


def test_index_sin_sesion(client):
    response = client.get('/clientes/')

    assert response.status_code == 302
    assert response.headers['Location'].startswith('/?next=')


# --------------------------------------------------------------------- add
def test_add_muestra_formulario(admin_client):
    response = admin_client.get('/clientes/add')

    assert response.status_code == 200
    assert b'name="nombre"' in response.data


def test_add_como_admin_crea_cliente(admin_client, app):
    from app.models.cliente import Cliente

    response = admin_client.post('/clientes/add', data={
        'nombre': 'Cliente Nuevo',
        'edad': '30',
        'telefono': '3005556677',
    })

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/clientes/')

    nuevo = Cliente.query.filter_by(nombre='Cliente Nuevo').first()
    assert nuevo is not None
    assert nuevo.edad == 30
    assert nuevo.telefono == '3005556677'


def test_add_como_usuario_usa_su_propio_nombre(user_client, normal_user, app):
    from app.models.cliente import Cliente

    response = user_client.post('/clientes/add', data={
        'nombre': 'Nombre Falso Ignorado',
        'edad': '22',
        'telefono': '3112223344',
    }, follow_redirects=True)

    assert response.status_code == 200

    cliente = Cliente.query.filter_by(nombre=normal_user.nombre).first()
    assert cliente is not None
    assert Cliente.query.filter_by(nombre='Nombre Falso Ignorado').first() is None


def test_add_sin_sesion(client, app):
    from app.models.cliente import Cliente

    antes = Cliente.query.count()

    response = client.post('/clientes/add', data={
        'nombre': 'No Debe Crearse',
        'edad': '20',
        'telefono': '000',
    })

    assert response.status_code == 302
    assert Cliente.query.count() == antes


# -------------------------------------------------------------------- edit
def test_edit_get(admin_client, cliente):
    response = admin_client.get(f'/clientes/edit/{cliente.idCliente}')

    assert response.status_code == 200
    assert cliente.nombre.encode() in response.data


def test_edit_como_admin(admin_client, cliente, app):
    response = admin_client.post(f'/clientes/edit/{cliente.idCliente}', data={
        'nombre': 'Cliente Editado',
        'edad': '40',
        'telefono': '3200001111',
    })

    assert response.status_code == 302
    assert cliente.nombre == 'Cliente Editado'
    assert cliente.edad == 40
    assert cliente.telefono == '3200001111'


def test_edit_como_entrenador_permitido(trainer_client, cliente):
    response = trainer_client.post(f'/clientes/edit/{cliente.idCliente}', data={
        'nombre': 'Editado Por Trainer',
        'edad': '33',
        'telefono': '3011112222',
    })

    assert response.status_code == 302
    assert cliente.nombre == 'Editado Por Trainer'


def test_edit_como_usuario_prohibido(user_client, cliente):
    response = user_client.get(f'/clientes/edit/{cliente.idCliente}', follow_redirects=True)

    assert response.status_code == 200
    assert b'No tienes permisos para editar clientes.' in response.data

    response_post = user_client.post(f'/clientes/edit/{cliente.idCliente}', data={
        'nombre': 'No Debe Cambiar',
        'edad': '1',
        'telefono': '1',
    }, follow_redirects=True)

    assert response_post.status_code == 200
    assert cliente.nombre == 'Cliente Uno'


def test_edit_id_inexistente(admin_client):
    response = admin_client.get('/clientes/edit/99999')

    # get_or_404 lanza NotFound y el handler global redirige al login
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')


def test_edit_sin_sesion(client, cliente):
    response = client.get(f'/clientes/edit/{cliente.idCliente}')

    assert response.status_code == 302
    assert response.headers['Location'].startswith('/?next=')


# ------------------------------------------------------------------ delete
def test_delete_como_admin(admin_client, cliente, app):
    from app.models.cliente import Cliente

    response = admin_client.post(f'/clientes/delete/{cliente.idCliente}', follow_redirects=True)

    assert response.status_code == 200
    assert b'Cliente eliminado con \xc3\xa9xito' in response.data
    assert Cliente.query.get(cliente.idCliente) is None


def test_delete_como_usuario_prohibido(user_client, cliente, app):
    from app.models.cliente import Cliente

    response = user_client.post(f'/clientes/delete/{cliente.idCliente}', follow_redirects=True)

    assert response.status_code == 200
    assert b'No tienes permisos para borrar clientes.' in response.data
    assert Cliente.query.get(cliente.idCliente) is not None


def test_delete_sin_sesion(client, cliente, app):
    from app.models.cliente import Cliente

    response = client.post(f'/clientes/delete/{cliente.idCliente}')

    assert response.status_code == 302
    assert Cliente.query.get(cliente.idCliente) is not None


# ------------------------------------------------------- asistencia clientes
def test_marcar_entrada_sin_sesion(client):
    response = client.get('/clientes/asistencia/marcar-entrada')

    assert response.status_code == 302
    assert response.headers['Location'].startswith('/?next=')


def test_marcar_entrada_registra_asistencia(user_client, normal_user, app):
    from app.models.asistencia_cliente import AsistenciaCliente

    response = user_client.get('/clientes/asistencia/marcar-entrada', follow_redirects=True)

    assert response.status_code == 200
    assert b'Tu entrada ha sido registrada.' in response.data

    asistencias = AsistenciaCliente.query.filter_by(idUser=normal_user.idUser).all()
    assert len(asistencias) == 1
    assert asistencias[0].hora_salida is None


def test_marcar_entrada_duplicada_bloqueada(user_client, normal_user, app):
    from app.models.asistencia_cliente import AsistenciaCliente

    user_client.get('/clientes/asistencia/marcar-entrada')
    response = user_client.get('/clientes/asistencia/marcar-entrada', follow_redirects=True)

    assert response.status_code == 200
    assert b'Ya has marcado entrada hoy.' in response.data

    asistencias = AsistenciaCliente.query.filter_by(idUser=normal_user.idUser).all()
    assert len(asistencias) == 1


def test_marcar_salida_propia(user_client, normal_user, asistencia_cliente_factory):
    asistencia = asistencia_cliente_factory(normal_user)

    response = user_client.get(
        f'/clientes/asistencia/marcar-salida/{asistencia.idAsistencia}',
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b'Tu salida ha sido registrada.' in response.data
    assert asistencia.hora_salida is not None


def test_marcar_salida_de_otro_usuario_prohibida(user_client, admin_user, asistencia_cliente_factory):
    asistencia = asistencia_cliente_factory(admin_user)

    response = user_client.get(
        f'/clientes/asistencia/marcar-salida/{asistencia.idAsistencia}',
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b'No puedes marcar la salida de otro usuario.' in response.data
    assert asistencia.hora_salida is None


def test_marcar_salida_id_inexistente(user_client):
    response = user_client.get('/clientes/asistencia/marcar-salida/99999')

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')


def test_historial_como_admin_ve_todo(admin_client, normal_user, admin_user, asistencia_cliente_factory):
    asistencia_cliente_factory(normal_user)
    asistencia_cliente_factory(admin_user)

    response = admin_client.get('/clientes/asistencia/historial')

    assert response.status_code == 200
    assert b'Registro de Entradas y Salidas' in response.data
    assert normal_user.nombre.encode() in response.data
    assert admin_user.nombre.encode() in response.data


def test_historial_como_usuario_ve_lo_suyo(user_client, normal_user, admin_user, asistencia_cliente_factory):
    asistencia_cliente_factory(normal_user)
    asistencia_cliente_factory(admin_user)

    response = user_client.get('/clientes/asistencia/historial')

    assert response.status_code == 200
    assert normal_user.nombre.encode() in response.data
    assert admin_user.nombre.encode() not in response.data


def test_historial_sin_sesion(client):
    response = client.get('/clientes/asistencia/historial')

    assert response.status_code == 302
    assert response.headers['Location'].startswith('/?next=')
