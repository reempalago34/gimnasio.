"""Pruebas del blueprint de planes (/planes/*)."""


# ------------------------------------------------------------------- index
def test_index_como_admin(admin_client, plan):
    response = admin_client.get('/planes/')

    assert response.status_code == 200
    assert b'Listado de Planes' in response.data
    assert plan.nombrePlan.encode() in response.data


def test_index_como_usuario_comun(user_client, plan):
    # El index es accesible para cualquier rol autenticado
    response = user_client.get('/planes/')

    assert response.status_code == 200
    assert plan.nombrePlan.encode() in response.data


def test_index_sin_sesion(client):
    response = client.get('/planes/')

    assert response.status_code == 302
    assert response.headers['Location'].startswith('/?next=')


# --------------------------------------------------------------------- add
def test_add_get_como_admin(admin_client):
    response = admin_client.get('/planes/add')

    assert response.status_code == 200
    assert b'name="nombrePlan"' in response.data
    assert b'name="precio"' in response.data


def test_add_get_como_entrenador_prohibido(trainer_client):
    response = trainer_client.get('/planes/add', follow_redirects=True)

    assert response.status_code == 200
    assert b'No tienes permisos para agregar planes.' in response.data


def test_add_post_como_admin(admin_client, app):
    from app.models.plan import Plan

    response = admin_client.post('/planes/add', data={
        'nombrePlan': 'Premium',
        'precio': '120000',
        'duracionMeses': '3',
    })

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/planes/')

    plan = Plan.query.filter_by(nombrePlan='Premium').first()
    assert plan is not None
    assert plan.precio == 120000.0
    assert plan.duracionMeses == 3


def test_add_post_como_recepcionista(staff_client, app):
    from app.models.plan import Plan

    response = staff_client.post('/planes/add', data={
        'nombrePlan': 'Intermedio',
        'precio': '80000',
        'duracionMeses': '1',
    })

    assert response.status_code == 302
    assert Plan.query.filter_by(nombrePlan='Intermedio').first() is not None


def test_add_post_como_entrenador_prohibido(trainer_client, app):
    from app.models.plan import Plan

    antes = Plan.query.count()

    response = trainer_client.post('/planes/add', data={
        'nombrePlan': 'No Debe Crearse',
        'precio': '1',
        'duracionMeses': '1',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'No tienes permisos para agregar planes.' in response.data
    assert Plan.query.count() == antes


def test_add_sin_sesion(client, app):
    from app.models.plan import Plan

    antes = Plan.query.count()

    response = client.post('/planes/add', data={
        'nombrePlan': 'X',
        'precio': '1',
        'duracionMeses': '1',
    })

    assert response.status_code == 302
    assert Plan.query.count() == antes


# -------------------------------------------------------------------- edit
def test_edit_get(admin_client, plan):
    response = admin_client.get(f'/planes/edit/{plan.idPlan}')

    assert response.status_code == 200
    assert plan.nombrePlan.encode() in response.data


def test_edit_post_como_admin(admin_client, plan):
    response = admin_client.post(f'/planes/edit/{plan.idPlan}', data={
        'nombrePlan': 'Basico Plus',
        'precio': '60000',
        'duracionMeses': '2',
    })

    assert response.status_code == 302
    assert plan.nombrePlan == 'Basico Plus'
    assert plan.precio == 60000.0
    assert plan.duracionMeses == 2


def test_edit_como_entrenador_prohibido(trainer_client, plan):
    response = trainer_client.post(f'/planes/edit/{plan.idPlan}', data={
        'nombrePlan': 'Hackeado',
        'precio': '1',
        'duracionMeses': '1',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'No tienes permisos para editar planes.' in response.data
    assert plan.nombrePlan == 'Basico'


def test_edit_id_inexistente(admin_client):
    response = admin_client.get('/planes/edit/99999')

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')


def test_edit_sin_sesion(client, plan):
    response = client.get(f'/planes/edit/{plan.idPlan}')

    assert response.status_code == 302
    assert response.headers['Location'].startswith('/?next=')


# ------------------------------------------------------------------ delete
def test_delete_como_admin(admin_client, plan, app):
    from app.models.plan import Plan

    response = admin_client.post(f'/planes/delete/{plan.idPlan}', follow_redirects=True)

    assert response.status_code == 200
    assert b'Plan eliminado con \xc3\xa9xito' in response.data
    assert Plan.query.get(plan.idPlan) is None


def test_delete_como_entrenador_prohibido(trainer_client, plan, app):
    from app.models.plan import Plan

    response = trainer_client.post(f'/planes/delete/{plan.idPlan}', follow_redirects=True)

    assert response.status_code == 200
    assert b'No tienes permisos para borrar planes.' in response.data
    assert Plan.query.get(plan.idPlan) is not None


def test_delete_sin_sesion(client, plan, app):
    from app.models.plan import Plan

    response = client.post(f'/planes/delete/{plan.idPlan}')

    assert response.status_code == 302
    assert Plan.query.get(plan.idPlan) is not None
