"""Pruebas de login y logout."""


def test_login_exitoso(client, normal_user):
    response = client.post('/', data={
        'nameUser': normal_user.nombre,
        'passwordUser': 'pass12345',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert '¡Hola, usuario_test!'.encode() in response.data


def test_login_credenciales_invalidas(client, normal_user):
    response = client.post('/', data={
        'nameUser': normal_user.nombre,
        'passwordUser': 'clave-mala',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid credentials. Please try again.' in response.data
    assert b'Iniciar Sesi' in response.data  # permanece en el login


def test_login_usuario_inexistente(client):
    response = client.post('/', data={
        'nameUser': 'no_existe',
        'passwordUser': 'cualquiera123',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid credentials. Please try again.' in response.data


def test_login_get_muestra_formulario(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'nameUser' in response.data
    assert b'passwordUser' in response.data


def test_usuario_ya_autenticado_se_redirige_al_dashboard(client, normal_user):
    client.post('/', data={
        'nameUser': normal_user.nombre,
        'passwordUser': 'pass12345',
    })

    response = client.get('/')

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/dashboard')


def test_dashboard_sin_sesion_redirige_a_login(client):
    response = client.get('/dashboard')

    assert response.status_code == 302
    # Flask-Login agrega ?next= para volver al dashboard tras el login
    assert response.headers['Location'].startswith('/?next=')


def test_logout(client, normal_user):
    client.post('/', data={
        'nameUser': normal_user.nombre,
        'passwordUser': 'pass12345',
    })

    response = client.get('/logout', follow_redirects=True)

    assert response.status_code == 200
    assert b'You have been logged out.' in response.data
    assert b'Iniciar Sesi' in response.data


def test_dashboard_sin_sesion_despues_de_logout(client, normal_user):
    client.post('/', data={
        'nameUser': normal_user.nombre,
        'passwordUser': 'pass12345',
    })
    client.get('/logout')

    response = client.get('/dashboard')

    assert response.status_code == 302
    assert response.headers['Location'].startswith('/?next=')


def test_dashboard_muestra_totales(admin_client, plan, cliente):
    response = admin_client.get('/dashboard')

    assert response.status_code == 200
    assert '¡Hola, admin_test!'.encode() in response.data
