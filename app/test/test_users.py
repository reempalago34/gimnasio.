"""Pruebas del blueprint de usuarios (/User/*) con control de roles."""


# ---------------------------------------------------------------- index / js
def test_index_como_admin(admin_client, normal_user):
    response = admin_client.get('/User/')

    assert response.status_code == 200
    assert 'Lista de Usuarios'.encode() in response.data
    assert normal_user.nombre.encode() in response.data


def test_index_como_usuario_no_admin(user_client):
    response = user_client.get('/User/', follow_redirects=True)

    assert response.status_code == 200
    assert 'No tienes permisos para acceder a esta secci'.encode() in response.data


def test_index_sin_sesion_redirige_a_login(client):
    response = client.get('/User/')

    assert response.status_code == 302
    assert response.headers['Location'].startswith('/?next=')


def test_indexjs_devuelve_json(admin_client, normal_user):
    response = admin_client.get('/User/js')

    assert response.status_code == 200
    data = response.get_json()
    nombres = [u['nombre'] for u in data]
    assert normal_user.nombre in nombres
    assert 'email' in data[0]
    assert 'rol' in data[0]


def test_indexjs_como_usuario_no_admin(user_client):
    response = user_client.get('/User/js')

    assert response.status_code == 302


# ---------------------------------------------------------------------- add
def test_add_muestra_formulario(client):
    response = client.get('/User/add')

    assert response.status_code == 200
    assert b'emailUser' in response.data
    assert b'confirmPassword' in response.data


def test_add_sin_email(client):
    response = client.post('/User/add', data={
        'nameUser': 'nuevo_user',
        'passwordUser': 'pass12345',
        'confirmPassword': 'pass12345',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Todos los campos son obligatorios' in response.data


def test_add_passwords_no_coinciden(client):
    response = client.post('/User/add', data={
        'nameUser': 'nuevo_user',
        'emailUser': 'nuevo@test.com',
        'passwordUser': 'pass12345',
        'confirmPassword': 'otra12345',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Las contrase' in response.data


def test_add_password_corta(client):
    response = client.post('/User/add', data={
        'nameUser': 'nuevo_user',
        'emailUser': 'nuevo@test.com',
        'passwordUser': 'abc',
        'confirmPassword': 'abc',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'6 caracteres' in response.data


def test_add_nombre_duplicado(client, normal_user):
    response = client.post('/User/add', data={
        'nameUser': normal_user.nombre,
        'emailUser': 'otro@test.com',
        'passwordUser': 'pass12345',
        'confirmPassword': 'pass12345',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'El nombre de usuario ya est' in response.data


def test_add_email_duplicado(client, normal_user):
    response = client.post('/User/add', data={
        'nameUser': 'otro_user',
        'emailUser': normal_user.email,
        'passwordUser': 'pass12345',
        'confirmPassword': 'pass12345',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'El correo electr' in response.data


def test_add_registro_publico_crea_y_autologin(client, app):
    from app.models.users import User

    response = client.post('/User/add', data={
        'nameUser': 'registrado',
        'emailUser': 'registrado@test.com',
        'telefonoUser': '3009998877',
        'passwordUser': 'pass12345',
        'confirmPassword': 'pass12345',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Cuenta creada correctamente' in response.data
    assert '¡Hola, registrado!'.encode() in response.data

    user = User.query.filter_by(nombre='registrado').first()
    assert user is not None
    assert user.rol == 'usuario'
    assert user.check_password('pass12345')
    assert user.email == 'registrado@test.com'


def test_add_como_admin_asigna_rol(admin_client, app):
    from app.models.users import User

    response = admin_client.post('/User/add', data={
        'nameUser': 'nuevo_entrenador',
        'emailUser': 'entrenador@test.com',
        'passwordUser': 'pass12345',
        'confirmPassword': 'pass12345',
        'rol': 'entrenador',
    })

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/User/')

    user = User.query.filter_by(nombre='nuevo_entrenador').first()
    assert user.rol == 'entrenador'
    assert 'Usuario creado correctamente por el administrador.' in _flashes(admin_client)


# --------------------------------------------------------------------- edit
def test_edit_get_propio(client, normal_user):
    _login(client, normal_user)

    response = client.get(f'/User/edit/{normal_user.idUser}')

    assert response.status_code == 200
    assert normal_user.nombre.encode() in response.data


def test_edit_get_de_otro_usuario_prohibido(client, normal_user, admin_user):
    _login(client, normal_user)

    response = client.get(f'/User/edit/{admin_user.idUser}', follow_redirects=True)

    assert response.status_code == 200
    assert b'No puedes editar otro usuario.' in response.data


def test_edit_propio_actualiza_nombre(client, normal_user, app):
    _login(client, normal_user)

    response = client.post(f'/User/edit/{normal_user.idUser}', data={
        'nameUser': 'usuario_renombrado',
        'emailUser': normal_user.email,
        'telefonoUser': '3111111111',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert normal_user.nombre == 'usuario_renombrado'
    assert b'Usuario actualizado correctamente.' in response.data
    assert b'usuario_renombrado' in response.data


def test_edit_nombre_duplicado(admin_client, normal_user, staff_user):
    response = admin_client.post(f'/User/edit/{normal_user.idUser}', data={
        'nameUser': staff_user.nombre,
        'emailUser': normal_user.email,
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'El nombre de usuario ya est' in response.data
    assert normal_user.nombre == 'usuario_test'


def test_edit_passwords_no_coinciden(client, normal_user):
    _login(client, normal_user)

    response = client.post(f'/User/edit/{normal_user.idUser}', data={
        'nameUser': normal_user.nombre,
        'passwordUser': 'nuevapass1',
        'confirmPassword': 'otrapass1',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Las contrase' in response.data
    assert normal_user.check_password('pass12345')


def test_edit_password_corta(client, normal_user):
    _login(client, normal_user)

    response = client.post(f'/User/edit/{normal_user.idUser}', data={
        'nameUser': normal_user.nombre,
        'passwordUser': 'abc',
        'confirmPassword': 'abc',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'6 caracteres' in response.data
    assert normal_user.check_password('pass12345')


def test_edit_admin_cambia_rol(admin_client, normal_user):
    response = admin_client.post(f'/User/edit/{normal_user.idUser}', data={
        'nameUser': normal_user.nombre,
        'emailUser': normal_user.email,
        'rol': 'recepcionista',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert normal_user.rol == 'recepcionista'


def test_edit_no_admin_no_puede_cambiar_rol(client, normal_user):
    _login(client, normal_user)

    client.post(f'/User/edit/{normal_user.idUser}', data={
        'nameUser': normal_user.nombre,
        'emailUser': normal_user.email,
        'rol': 'admin',
    })

    assert normal_user.rol == 'usuario'


def test_edit_sin_sesion_redirige_a_login(client, normal_user):
    response = client.get(f'/User/edit/{normal_user.idUser}')

    assert response.status_code == 302
    assert response.headers['Location'].startswith('/?next=')


# ------------------------------------------------------------------- detail
def test_detail_propio(client, normal_user):
    _login(client, normal_user)

    response = client.get(f'/User/detail/{normal_user.idUser}')

    assert response.status_code == 200
    assert f'Usuario {normal_user.nombre}'.encode() in response.data


def test_detail_como_admin_de_otro(admin_client, normal_user):
    response = admin_client.get(f'/User/detail/{normal_user.idUser}')

    assert response.status_code == 200
    assert normal_user.email.encode() in response.data


def test_detail_de_otro_sin_permisos(client, normal_user, admin_user):
    _login(client, normal_user)

    response = client.get(f'/User/detail/{admin_user.idUser}', follow_redirects=True)

    assert response.status_code == 200
    assert b'No tienes permisos para ver este usuario.' in response.data


def test_detail_sin_sesion(client, normal_user):
    response = client.get(f'/User/detail/{normal_user.idUser}')

    assert response.status_code == 302
    assert response.headers['Location'].startswith('/?next=')


# ------------------------------------------------------------------- delete
def test_delete_como_admin(admin_client, normal_user):
    from app.models.users import User

    response = admin_client.post(f'/User/delete/{normal_user.idUser}', follow_redirects=True)

    assert response.status_code == 200
    assert b'Usuario eliminado correctamente.' in response.data
    assert User.query.get(normal_user.idUser) is None


def test_delete_de_otro_usuario_prohibido(client, normal_user, staff_user):
    from app.models.users import User

    _login(client, normal_user)

    response = client.post(f'/User/delete/{staff_user.idUser}', follow_redirects=True)

    assert response.status_code == 200
    assert b'No tienes permisos para eliminar este usuario.' in response.data
    assert User.query.get(staff_user.idUser) is not None


def test_delete_sin_sesion(client, normal_user):
    from app.models.users import User

    response = client.post(f'/User/delete/{normal_user.idUser}')

    assert response.status_code == 302
    assert response.headers['Location'].startswith('/?next=')
    assert User.query.get(normal_user.idUser) is not None


# ------------------------------------------------------------------ helpers
def _login(client, user):
    return client.post('/', data={
        'nameUser': user.nombre,
        'passwordUser': 'pass12345',
    })


def _flashes(client):
    """Devuelve el HTML del último render (para revisar mensajes flash)."""
    response = client.get('/dashboard')
    return response.get_data(as_text=True)
