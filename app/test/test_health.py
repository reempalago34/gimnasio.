"""Pruebas del health check, favicon y manejo global de errores."""


def test_health_ok(client):
    response = client.get('/health')

    assert response.status_code == 200
    assert response.get_json() == {'status': 'healthy'}


def test_health_unhealthy(client, monkeypatch):
    from app import db

    def _boom(*args, **kwargs):
        raise RuntimeError('conexion a BD rota')

    monkeypatch.setattr(db.session, 'execute', _boom)

    response = client.get('/health')

    assert response.status_code == 503
    assert response.get_json() == {'status': 'unhealthy'}


def test_favicon_no_existente_redirige_al_login(client):
    # app/static/favicon.ico no existe: el 404 cae en el handler global que
    # redirige a / (login) en lugar de devolver un 404 tradicional.
    response = client.get('/favicon.ico')

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')


def test_ruta_inexistente_redirige_al_login(client):
    response = client.get('/ruta-que-no-existe')

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')


def test_ruta_inexistente_con_redirect_llega_al_login(client):
    response = client.get('/ruta-que-no-existe', follow_redirects=True)

    assert response.status_code == 200
    assert 'Iniciar Sesión'.encode() in response.data


def test_excepcion_no_controlada_devuelve_500_json(admin_client, monkeypatch):
    from app.models.plan import Plan

    class _QueryRota:
        def all(self):
            raise RuntimeError('fallo simulado de base de datos')

    monkeypatch.setattr(Plan, 'query', _QueryRota())

    response = admin_client.get('/planes/')

    assert response.status_code == 500
    assert 'error' in response.get_json()
