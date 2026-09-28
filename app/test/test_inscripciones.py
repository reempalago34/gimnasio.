"""Pruebas del blueprint de inscripciones (/inscripciones/*)."""


# ------------------------------------------------------------------- index
def test_index_como_admin(admin_client, inscripcion_factory, cliente, plan):
    inscripcion_factory(cliente, plan)

    response = admin_client.get('/inscripciones/')

    assert response.status_code == 200
    assert b'Listado de Inscripciones' in response.data
    assert cliente.nombre.encode() in response.data
    assert plan.nombrePlan.encode() in response.data


def test_index_como_recepcionista(staff_client, inscripcion_factory, cliente, plan):
    inscripcion_factory(cliente, plan)

    response = staff_client.get('/inscripciones/')

    assert response.status_code == 200
    assert cliente.nombre.encode() in response.data


def test_index_como_usuario_solo_ve_las_suyas(
    user_client, normal_user, cliente_factory, inscripcion_factory, plan
):
    mio = cliente_factory(nombre=normal_user.nombre)
    inscripcion_factory(mio, plan)
    ajeno = cliente_factory(nombre='Cliente Ajeno')
    inscripcion_factory(ajeno, plan)

    response = user_client.get('/inscripciones/')

    assert response.status_code == 200
    assert b'Cliente Ajeno' not in response.data


def test_index_como_entrenador_prohibido(trainer_client):
    response = trainer_client.get('/inscripciones/', follow_redirects=True)

    assert response.status_code == 200
    assert b'No tienes permisos para ver esta secci' in response.data


def test_index_sin_sesion(client):
    response = client.get('/inscripciones/')

    assert response.status_code == 302
    assert response.headers['Location'].startswith('/?next=')


# ------------------------------------------------------------------ add GET
def test_add_get_como_admin(admin_client, plan, horario):
    response = admin_client.get('/inscripciones/add')

    assert response.status_code == 200
    assert b'name="terminos"' in response.data
    assert plan.nombrePlan.encode() in response.data


def test_add_get_con_inscripcion_previa_lo_bloquea(
    user_client, normal_user, cliente_factory, inscripcion_factory, plan
):
    cliente = cliente_factory(nombre=normal_user.nombre)
    inscripcion_factory(cliente, plan)

    response = user_client.get('/inscripciones/add', follow_redirects=True)

    assert response.status_code == 200
    assert b'Ya tienes una inscripci\xc3\xb3n activa. Debes cancelarla para cambiar de plan.' in response.data


def test_add_sin_sesion(client):
    response = client.get('/inscripciones/add')

    assert response.status_code == 302
    assert response.headers['Location'].startswith('/?next=')


# ----------------------------------------------------------------- add POST
def test_add_post_como_admin_crea_todo(admin_client, plan, horario, app):
    from app.models.cliente import Cliente
    from app.models.horario import Horario
    from app.models.inscripcion import Inscripcion
    from app.models.pago import Pago

    response = admin_client.post('/inscripciones/add', data={
        'nombre': 'Cliente Inscribido',
        'email': 'inscrito@test.com',
        'edad': '28',
        'telefono': '3007778899',
        'idPlan': str(plan.idPlan),
        'idHorario': str(horario.idHorario),
        'terminos': 'on',
    })

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/inscripciones/')

    cliente = Cliente.query.filter_by(nombre='Cliente Inscribido').first()
    assert cliente is not None
    assert cliente.email == 'inscrito@test.com'

    inscripcion = Inscripcion.query.filter_by(idCliente=cliente.idCliente).first()
    assert inscripcion is not None
    assert inscripcion.idPlan == plan.idPlan

    # El pago automático se genera con el precio del plan
    pago = Pago.query.filter_by(idInscripcion=inscripcion.idInscripcion).first()
    assert pago is not None
    assert pago.metodo_pago == 'Automático (Inscripción)'
    assert pago.monto == plan.precio

    # El horario quedó vinculado al usuario que hizo la inscripción
    horario_r = Horario.query.get(horario.idHorario)
    assert any(u.rol == 'admin' for u in horario_r.usuarios_inscritos)


def test_add_post_sin_terminos_no_inscribe(admin_client, plan, app):
    from app.models.inscripcion import Inscripcion

    antes = Inscripcion.query.count()

    response = admin_client.post('/inscripciones/add', data={
        'nombre': 'Sin Terminos',
        'email': 'sin@test.com',
        'edad': '20',
        'telefono': '1',
        'idPlan': str(plan.idPlan),
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Debes aceptar los t' in response.data
    assert Inscripcion.query.count() == antes


def test_add_post_como_usuario_usa_su_nombre(
    user_client, normal_user, plan, app
):
    from app.models.cliente import Cliente
    from app.models.inscripcion import Inscripcion

    response = user_client.post('/inscripciones/add', data={
        'nombre': 'Nombre Ignorado',
        'email': normal_user.email,
        'edad': '25',
        'telefono': '3000001111',
        'idPlan': str(plan.idPlan),
        'terminos': 'on',
    }, follow_redirects=True)

    assert response.status_code == 200

    cliente = Cliente.query.filter_by(nombre=normal_user.nombre).first()
    assert cliente is not None
    assert Cliente.query.filter_by(nombre='Nombre Ignorado').first() is None

    inscripcion = Inscripcion.query.filter_by(idCliente=cliente.idCliente).first()
    assert inscripcion is not None


def test_add_post_cliente_ya_inscripto_como_admin_bloqueado(
    admin_client, cliente, inscripcion_factory, plan, app
):
    from app.models.inscripcion import Inscripcion

    inscripcion_factory(cliente, plan)
    antes = Inscripcion.query.count()

    response = admin_client.post('/inscripciones/add', data={
        'nombre': cliente.nombre,
        'email': 'x@test.com',
        'edad': '30',
        'telefono': '1',
        'idPlan': str(plan.idPlan),
        'terminos': 'on',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'El usuario ya tiene una inscripci\xc3\xb3n activa.' in response.data
    assert Inscripcion.query.count() == antes


def test_add_post_usuario_ya_inscripto_bloqueado(
    user_client, normal_user, cliente_factory, inscripcion_factory, plan, app
):
    from app.models.inscripcion import Inscripcion

    cliente = cliente_factory(nombre=normal_user.nombre)
    inscripcion_factory(cliente, plan)
    antes = Inscripcion.query.count()

    response = user_client.post('/inscripciones/add', data={
        'idPlan': str(plan.idPlan),
        'terminos': 'on',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Ya tienes una inscripci\xc3\xb3n activa.' in response.data
    assert Inscripcion.query.count() == antes


def test_add_post_sin_sesion(client, plan, app):
    from app.models.inscripcion import Inscripcion

    antes = Inscripcion.query.count()

    response = client.post('/inscripciones/add', data={
        'nombre': 'Anon',
        'edad': '20',
        'idPlan': str(plan.idPlan),
        'terminos': 'on',
    })

    assert response.status_code == 302
    assert Inscripcion.query.count() == antes


# ------------------------------------------------------------------ delete
def test_delete_como_admin(admin_client, inscripcion_factory, cliente, plan, app):
    from app.models.inscripcion import Inscripcion

    inscripcion = inscripcion_factory(cliente, plan)

    response = admin_client.post(
        f'/inscripciones/delete/{inscripcion.idInscripcion}',
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b'Inscripci\xc3\xb3n cancelada con \xc3\xa9xito' in response.data
    assert Inscripcion.query.get(inscripcion.idInscripcion) is None


def test_delete_como_duenio(user_client, normal_user, cliente_factory, inscripcion_factory, plan, app):
    from app.models.inscripcion import Inscripcion

    cliente = cliente_factory(nombre=normal_user.nombre)
    inscripcion = inscripcion_factory(cliente, plan)

    response = user_client.post(
        f'/inscripciones/delete/{inscripcion.idInscripcion}',
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert Inscripcion.query.get(inscripcion.idInscripcion) is None


def test_delete_de_otro_usuario_prohibido(
    user_client, normal_user, cliente_factory, inscripcion_factory, plan, app
):
    from app.models.inscripcion import Inscripcion

    ajeno = cliente_factory(nombre='Cliente Ajeno')
    inscripcion = inscripcion_factory(ajeno, plan)

    response = user_client.post(
        f'/inscripciones/delete/{inscripcion.idInscripcion}',
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b'No tienes permiso para realizar esta acci\xc3\xb3n.' in response.data
    assert Inscripcion.query.get(inscripcion.idInscripcion) is not None


def test_delete_como_entrenador_prohibido(trainer_client, inscripcion_factory, cliente, plan, app):
    from app.models.inscripcion import Inscripcion

    inscripcion = inscripcion_factory(cliente, plan)

    response = trainer_client.post(
        f'/inscripciones/delete/{inscripcion.idInscripcion}',
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b'No tienes permiso para realizar esta acci\xc3\xb3n.' in response.data
    assert Inscripcion.query.get(inscripcion.idInscripcion) is not None


def test_delete_sin_sesion(client, inscripcion_factory, cliente, plan, app):
    from app.models.inscripcion import Inscripcion

    inscripcion = inscripcion_factory(cliente, plan)

    response = client.post(f'/inscripciones/delete/{inscripcion.idInscripcion}')

    assert response.status_code == 302
    assert Inscripcion.query.get(inscripcion.idInscripcion) is not None
