"""Pruebas de recuperación de contraseña (forgot/reset password)."""


def test_forgot_password_muestra_formulario(client):
    response = client.get('/forgot-password')

    assert response.status_code == 200
    assert b'Recuperar Contrase' in response.data
    assert b'name="email"' in response.data


def test_forgot_password_envia_correo_con_token(client, normal_user, mock_email):
    response = client.post('/forgot-password', data={'email': normal_user.email})

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')

    assert len(mock_email) == 1
    assert mock_email[0]['to'] == normal_user.email
    assert '/reset-password/' in mock_email[0]['cuerpo']


def test_forgot_password_flash_mismo_mensaje_para_correo_inexistente(client, mock_email):
    response = client.post(
        '/forgot-password',
        data={'email': 'nadie@test.com'},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert 'Si el correo está registrado'.encode() in response.data
    assert mock_email == []


def test_forgot_password_autenticado_redirige_al_dashboard(admin_client):
    response = admin_client.get('/forgot-password')

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/dashboard')


def test_reset_password_formulario_valido(client, normal_user, mock_email):
    client.post('/forgot-password', data={'email': normal_user.email})
    token = _extraer_token(mock_email[0]['cuerpo'])

    response = client.get(f'/reset-password/{token}')

    assert response.status_code == 200
    assert b'Nueva Contrase' in response.data
    assert b'name="password"' in response.data


def test_reset_password_token_invalido_redirige(client):
    response = client.get('/reset-password/token-falso-123')

    assert response.status_code == 302
    assert '/forgot-password' in response.headers['Location']


def test_reset_password_contrasena_corta(client, normal_user, mock_email):
    token = _token_para(client, normal_user, mock_email)

    response = client.post(f'/reset-password/{token}', data={
        'password': 'abc',
        'confirmPassword': 'abc',
    })

    assert response.status_code == 200
    assert 'La contraseña debe tener al menos 6 caracteres.'.encode() in response.data
    assert normal_user.check_password('pass12345')


def test_reset_password_no_coinciden(client, normal_user, mock_email):
    token = _token_para(client, normal_user, mock_email)

    response = client.post(f'/reset-password/{token}', data={
        'password': 'nuevapass1',
        'confirmPassword': 'otrapass1',
    })

    assert response.status_code == 200
    assert b'Las contrase' in response.data
    assert normal_user.check_password('pass12345')


def test_reset_password_exitoso_cambia_la_password(client, normal_user, mock_email):
    token = _token_para(client, normal_user, mock_email)

    response = client.post(f'/reset-password/{token}', data={
        'password': 'nuevapass1',
        'confirmPassword': 'nuevapass1',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Tu contrase' in response.data

    # La password vieja deja de servir y la nueva funciona
    r_vieja = client.post('/', data={
        'nameUser': normal_user.nombre,
        'passwordUser': 'pass12345',
    }, follow_redirects=True)
    assert b'Invalid credentials. Please try again.' in r_vieja.data

    r_nueva = client.post('/', data={
        'nameUser': normal_user.nombre,
        'passwordUser': 'nuevapass1',
    }, follow_redirects=True)
    assert r_nueva.status_code == 200
    assert '¡Hola, usuario_test!'.encode() in r_nueva.data


def test_reset_password_autenticado_redirige_al_dashboard(admin_client):
    response = admin_client.get('/reset-password/cualquier-token')

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/dashboard')


def _extraer_token(cuerpo):
    # El link viene en el HTML: href="http://.../reset-password/<token>"
    inicio = cuerpo.index('/reset-password/') + len('/reset-password/')
    fin = cuerpo.index('"', inicio)
    return cuerpo[inicio:fin]


def _token_para(client, user, mock_email):
    client.post('/forgot-password', data={'email': user.email})
    return _extraer_token(mock_email[-1]['cuerpo'])
