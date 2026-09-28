"""Pruebas de la API JSON de usuarios (/UserAsync/*)."""

import pytest


# ------------------------------------------------------------------- index
def test_index_como_admin(admin_client, normal_user):
    response = admin_client.get('/UserAsync/index')

    assert response.status_code == 200
    nombres = [u['nombre'] for u in response.get_json()]
    assert normal_user.nombre in nombres


def test_index_como_usuario_comun(user_client, normal_user):
    # Cualquier usuario autenticado puede listar
    response = user_client.get('/UserAsync/index')

    assert response.status_code == 200
    nombres = [u['nombre'] for u in response.get_json()]
    assert normal_user.nombre in nombres


def test_index_sin_sesion(client):
    response = client.get('/UserAsync/index')

    assert response.status_code == 302
    assert response.headers['Location'].startswith('/?next=')


# --------------------------------------------------------------------- add
def test_add_como_no_admin_devuelve_403(user_client):
    response = user_client.post('/UserAsync/add', json={
        'nameUser': 'otro',
        'passwordUser': 'pass12345',
    })

    assert response.status_code == 403
    assert response.get_json() == {'message': 'Unauthorized'}


def test_add_sin_sesion(client):
    response = client.post('/UserAsync/add', json={
        'nameUser': 'otro',
        'passwordUser': 'pass12345',
    })

    assert response.status_code == 302


@pytest.mark.xfail(
    reason='BUG: POST /UserAsync/add no envia el email (columna NOT NULL) y termina en 500',
    strict=False,
)
def test_add_como_admin_crea_usuario(admin_client):
    from app.models.users import User

    response = admin_client.post('/UserAsync/add', json={
        'nameUser': 'async_admin',
        'passwordUser': 'pass12345',
    })

    assert response.status_code == 201
    assert response.get_json() == {'message': 'User created successfully'}
    assert User.query.filter_by(nombre='async_admin').first() is not None


# ------------------------------------------------------------------ update
def test_update_propio(user_client, normal_user):
    response = user_client.put(f'/UserAsync/update/{normal_user.idUser}', json={
        'nameUser': 'usuario_async_editado',
    })

    assert response.status_code == 200
    assert response.get_json() == {'message': 'User updated successfully'}
    assert normal_user.nombre == 'usuario_async_editado'


def test_update_propio_con_password(user_client, normal_user):
    response = user_client.put(f'/UserAsync/update/{normal_user.idUser}', json={
        'nameUser': normal_user.nombre,
        'passwordUser': 'nuevapass1',
    })

    assert response.status_code == 200
    assert normal_user.check_password('nuevapass1')


def test_update_de_otro_usuario_no_admin_403(user_client, staff_user):
    response = user_client.put(f'/UserAsync/update/{staff_user.idUser}', json={
        'nameUser': 'hackeado',
    })

    assert response.status_code == 403
    assert response.get_json() == {'message': 'Unauthorized'}
    assert staff_user.nombre == 'recepcionista_test'


def test_update_como_admin_de_otro(admin_client, normal_user):
    response = admin_client.put(f'/UserAsync/update/{normal_user.idUser}', json={
        'nameUser': 'editado_por_admin',
    })

    assert response.status_code == 200
    assert normal_user.nombre == 'editado_por_admin'


def test_update_id_inexistente_404(admin_client):
    response = admin_client.put('/UserAsync/update/99999', json={
        'nameUser': 'fantasma',
    })

    assert response.status_code == 404
    assert response.get_json() == {'message': 'User not found'}


def test_update_sin_sesion(client, normal_user):
    response = client.put(f'/UserAsync/update/{normal_user.idUser}', json={
        'nameUser': 'x',
    })

    assert response.status_code == 302


# ------------------------------------------------------------------ delete
def test_delete_como_no_admin_403(user_client, staff_user):
    from app.models.users import User

    response = user_client.delete(f'/UserAsync/delete/{staff_user.idUser}')

    assert response.status_code == 403
    assert User.query.get(staff_user.idUser) is not None


def test_delete_como_admin(admin_client, normal_user):
    from app.models.users import User

    response = admin_client.delete(f'/UserAsync/delete/{normal_user.idUser}')

    assert response.status_code == 200
    assert response.get_json() == {'message': 'User deleted successfully'}
    assert User.query.get(normal_user.idUser) is None


def test_delete_id_inexistente_404(admin_client):
    response = admin_client.delete('/UserAsync/delete/99999')

    assert response.status_code == 404
    assert response.get_json() == {'message': 'User not found'}


def test_delete_sin_sesion(client, normal_user):
    from app.models.users import User

    response = client.delete(f'/UserAsync/delete/{normal_user.idUser}')

    assert response.status_code == 302
    assert User.query.get(normal_user.idUser) is not None
