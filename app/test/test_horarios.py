"""Pruebas del blueprint de horarios y asistencia del entrenador (/horarios/*)."""


# ------------------------------------------------------------------- index
def test_index_como_admin(admin_client, horario):
    response = admin_client.get('/horarios/')

    assert response.status_code == 200
    assert b'Horarios de Entrenadores' in response.data
    assert horario.dia_semana.encode() in response.data


def test_index_entrenador_solo_ve_los_suyos(
    trainer_client, trainer_user, make_user, horario_factory
):
    otro_trainer = make_user('entrenador_dos', rol='entrenador')
    horario_factory(otro_trainer, dia='Viernes')

    response = trainer_client.get('/horarios/')

    assert response.status_code == 200
    assert trainer_user.nombre.encode() in response.data
    assert b'entrenador_dos' not in response.data
    assert b'Viernes' not in response.data


def test_index_sin_sesion(client):
    response = client.get('/horarios/')

    assert response.status_code == 302
    assert response.headers['Location'].startswith('/?next=')


# ------------------------------------------------------- asistencia entrada
def test_marcar_entrada_como_no_entrenador_prohibido(admin_client, horario):
    response = admin_client.get(
        f'/horarios/asistencia/marcar-entrada/{horario.idHorario}',
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b'Solo los entrenadores pueden marcar asistencia.' in response.data


def test_marcar_entrada_registra_asistencia(trainer_client, trainer_user, horario, app):
    from app.models.asistencia import AsistenciaEntrenador

    response = trainer_client.get(
        f'/horarios/asistencia/marcar-entrada/{horario.idHorario}',
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b'Entrada registrada con \xc3\xa9xito.' in response.data

    asistencias = AsistenciaEntrenador.query.filter_by(idUser=trainer_user.idUser).all()
    assert len(asistencias) == 1
    assert asistencias[0].hora_salida is None


def test_marcar_entrada_duplicada_bloqueada(trainer_client, trainer_user, horario, app):
    from app.models.asistencia import AsistenciaEntrenador

    trainer_client.get(f'/horarios/asistencia/marcar-entrada/{horario.idHorario}')
    response = trainer_client.get(
        f'/horarios/asistencia/marcar-entrada/{horario.idHorario}',
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b'Ya has marcado entrada para este horario hoy.' in response.data

    asistencias = AsistenciaEntrenador.query.filter_by(idUser=trainer_user.idUser).all()
    assert len(asistencias) == 1


def test_marcar_entrada_sin_sesion(client, horario):
    response = client.get(f'/horarios/asistencia/marcar-entrada/{horario.idHorario}')

    assert response.status_code == 302
    assert response.headers['Location'].startswith('/?next=')


# ------------------------------------------------------- asistencia salida
def test_marcar_salida_propia(trainer_client, trainer_user, horario, asistencia_entrenador_factory, app):
    asistencia = asistencia_entrenador_factory(trainer_user, horario)

    response = trainer_client.get(
        f'/horarios/asistencia/marcar-salida/{asistencia.idAsistencia}',
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b'Salida registrada con \xc3\xa9xito.' in response.data
    assert asistencia.hora_salida is not None


def test_marcar_salida_de_otro_entrenador_prohibida(
    trainer_client, make_user, horario_factory, asistencia_entrenador_factory, app
):
    otro = make_user('entrenador_dos', rol='entrenador')
    otro_horario = horario_factory(otro)
    asistencia = asistencia_entrenador_factory(otro, otro_horario)

    response = trainer_client.get(
        f'/horarios/asistencia/marcar-salida/{asistencia.idAsistencia}',
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b'No puedes marcar la salida de otro entrenador.' in response.data
    assert asistencia.hora_salida is None


def test_marcar_salida_id_inexistente(trainer_client):
    response = trainer_client.get('/horarios/asistencia/marcar-salida/99999')

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')


# ---------------------------------------------------------------- historial
def test_historial_como_admin(admin_client, trainer_user, horario, asistencia_entrenador_factory):
    asistencia_entrenador_factory(trainer_user, horario)

    response = admin_client.get('/horarios/historial')

    assert response.status_code == 200
    assert b'Historial de Asistencia' in response.data
    assert trainer_user.nombre.encode() in response.data


def test_historial_entrenador_ve_lo_suyo(
    trainer_client, trainer_user, make_user, horario_factory, asistencia_entrenador_factory
):
    asistencia_entrenador_factory(trainer_user, horario_factory(trainer_user))
    otro = make_user('entrenador_dos', rol='entrenador')
    asistencia_entrenador_factory(otro, horario_factory(otro, dia='Viernes'))

    response = trainer_client.get('/horarios/historial')

    assert response.status_code == 200
    assert trainer_user.nombre.encode() in response.data
    assert b'entrenador_dos' not in response.data


def test_historial_como_recepcionista_prohibido(staff_client):
    response = staff_client.get('/horarios/historial', follow_redirects=True)

    assert response.status_code == 200
    assert b'No tienes permisos para ver el historial.' in response.data


def test_historial_sin_sesion(client):
    response = client.get('/horarios/historial')

    assert response.status_code == 302
    assert response.headers['Location'].startswith('/?next=')


# ------------------------------------------------------ seleccionar horario
def test_seleccionar_horario(user_client, normal_user, horario, app):
    response = user_client.get(f'/horarios/seleccionar/{horario.idHorario}', follow_redirects=True)

    assert response.status_code == 200
    assert b'Has seleccionado el horario' in response.data
    assert normal_user in horario.usuarios_inscritos


def test_seleccionar_horario_dos_veces(user_client, normal_user, horario, app):
    user_client.get(f'/horarios/seleccionar/{horario.idHorario}')
    response = user_client.get(f'/horarios/seleccionar/{horario.idHorario}', follow_redirects=True)

    assert response.status_code == 200
    assert b'Ya tienes seleccionado este horario.' in response.data
    assert horario.usuarios_inscritos.count(normal_user) == 1


def test_seleccionar_id_inexistente(user_client):
    response = user_client.get('/horarios/seleccionar/99999')

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')


def test_seleccionar_sin_sesion(client, horario):
    response = client.get(f'/horarios/seleccionar/{horario.idHorario}')

    assert response.status_code == 302
    assert response.headers['Location'].startswith('/?next=')


def test_deseleccionar_horario(user_client, normal_user, horario, app):
    user_client.get(f'/horarios/seleccionar/{horario.idHorario}')

    response = user_client.get(f'/horarios/deseleccionar/{horario.idHorario}', follow_redirects=True)

    assert response.status_code == 200
    assert b'Horario removido de tu lista.' in response.data
    assert normal_user not in horario.usuarios_inscritos


def test_deseleccionar_sinSeleccionar_no_falla(user_client, normal_user, horario, app):
    response = user_client.get(f'/horarios/deseleccionar/{horario.idHorario}', follow_redirects=True)

    assert response.status_code == 200
    assert normal_user not in horario.usuarios_inscritos


# ---------------------------------------------------------------------- add
def test_add_get_como_admin(admin_client, trainer_user):
    response = admin_client.get('/horarios/add')

    assert response.status_code == 200
    assert b'name="dia_semana"' in response.data
    assert trainer_user.nombre.encode() in response.data


def test_add_post_como_admin(admin_client, trainer_user, app):
    from app.models.horario import Horario

    response = admin_client.post('/horarios/add', data={
        'idUser': str(trainer_user.idUser),
        'dia_semana': 'Miércoles',
        'hora_inicio': '10:00',
        'hora_fin': '11:00',
    })

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/horarios/')

    horario = Horario.query.filter_by(dia_semana='Miércoles').first()
    assert horario is not None
    assert horario.idUser == trainer_user.idUser
    assert horario.hora_inicio == '10:00'


def test_add_como_entrenador_prohibido(trainer_client, trainer_user, app):
    from app.models.horario import Horario

    antes = Horario.query.count()

    response = trainer_client.post('/horarios/add', data={
        'idUser': str(trainer_user.idUser),
        'dia_semana': 'Lunes',
        'hora_inicio': '07:00',
        'hora_fin': '08:00',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Solo el administrador puede asignar horarios.' in response.data
    assert Horario.query.count() == antes


def test_add_sin_sesion(client, trainer_user, app):
    from app.models.horario import Horario

    antes = Horario.query.count()

    response = client.post('/horarios/add', data={
        'idUser': str(trainer_user.idUser),
        'dia_semana': 'Lunes',
        'hora_inicio': '07:00',
        'hora_fin': '08:00',
    })

    assert response.status_code == 302
    assert Horario.query.count() == antes


# --------------------------------------------------------------------- edit
def test_edit_get_como_admin(admin_client, horario):
    response = admin_client.get(f'/horarios/edit/{horario.idHorario}')

    assert response.status_code == 200
    assert horario.dia_semana.encode() in response.data


def test_edit_post_como_admin(admin_client, horario):
    response = admin_client.post(f'/horarios/edit/{horario.idHorario}', data={
        'idUser': str(horario.idUser),
        'dia_semana': 'Jueves',
        'hora_inicio': '14:00',
        'hora_fin': '15:00',
    })

    assert response.status_code == 302
    assert horario.dia_semana == 'Jueves'
    assert horario.hora_inicio == '14:00'
    assert horario.hora_fin == '15:00'


def test_edit_como_entrenador_prohibido(trainer_client, horario):
    response = trainer_client.post(f'/horarios/edit/{horario.idHorario}', data={
        'idUser': str(horario.idUser),
        'dia_semana': 'Domingo',
        'hora_inicio': '00:00',
        'hora_fin': '01:00',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Solo el administrador puede editar horarios.' in response.data
    assert horario.dia_semana == 'Lunes'


def test_edit_id_inexistente(admin_client):
    response = admin_client.get('/horarios/edit/99999')

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')


def test_edit_sin_sesion(client, horario):
    response = client.get(f'/horarios/edit/{horario.idHorario}')

    assert response.status_code == 302
    assert response.headers['Location'].startswith('/?next=')


# ------------------------------------------------------------------- delete
def test_delete_como_admin(admin_client, horario, app):
    from app.models.horario import Horario

    response = admin_client.post(f'/horarios/delete/{horario.idHorario}', follow_redirects=True)

    assert response.status_code == 200
    assert b'Horario eliminado correctamente' in response.data
    assert Horario.query.get(horario.idHorario) is None


def test_delete_como_entrenador_prohibido(trainer_client, horario, app):
    from app.models.horario import Horario

    response = trainer_client.post(f'/horarios/delete/{horario.idHorario}', follow_redirects=True)

    assert response.status_code == 200
    assert b'No tienes permisos para borrar horarios.' in response.data
    assert Horario.query.get(horario.idHorario) is not None


def test_delete_sin_sesion(client, horario, app):
    from app.models.horario import Horario

    response = client.post(f'/horarios/delete/{horario.idHorario}')

    assert response.status_code == 302
    assert Horario.query.get(horario.idHorario) is not None
