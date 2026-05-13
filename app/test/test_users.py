def test_index(client):
    response = client.get('/User/')
    assert response.status_code == 200
    assert b"Usuarios" in response.data  # Asumiendo que hay un texto "Users" en la página

def test_add_user(client):
    response = client.post('/User/add', data={
        'nameUser': 'new_user',
        'passwordUser': 'new_password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Usuarios" in response.data  # Asumiendo que el nombre del usuario se muestra en la página

def test_edit_user(client, user):
    # Iniciar sesión como el mismo usuario antes de editar
    client.post('/', data={
        'nameUser': user.nameUser,
        'passwordUser': 'test_password'
    }, follow_redirects=True)

    response = client.post(f'/User/edit/{user.idUser}', data={
        'nameUser': 'updated_user',
        'passwordUser': 'updated_password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"updated_user" in response.data  # Asumiendo que el nombre del usuario actualizado se muestra en la página

def test_delete_user(client, user):
    # Iniciar sesión como el mismo usuario antes de eliminar
    client.post('/', data={
        'nameUser': user.nameUser,
        'passwordUser': 'test_password'
    }, follow_redirects=True)

    response = client.post(f'/User/delete/{user.idUser}', follow_redirects=True)
    assert response.status_code == 200
    assert b"Usuarios" in response.data  # Asumiendo que hay un mensaje de confirmación de eliminación

