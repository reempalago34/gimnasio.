import pytest

from app import create_app, db
from app.models.users import User


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'PROPAGATE_EXCEPTIONS': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key',
        # Desactivar el seed del admin para tener datos 100% controlados por los fixtures
        'ADMIN_NAME': '',
        'ADMIN_EMAIL': '',
        'ADMIN_PASSWORD': '',
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_client(app):
    def _make(user=None):
        c = app.test_client()
        if user is not None:
            c.post('/', data={'nameUser': user.nombre, 'passwordUser': 'pass12345'})
        return c

    return _make


@pytest.fixture
def make_user(app):
    def _make(nombre, rol='usuario', password='pass12345', email=None, telefono='3000000000'):
        user = User(
            nombre=nombre,
            email=email or f'{nombre}@test.com',
            rol=rol,
            telefono=telefono,
        )
        user.passwordUser = password
        db.session.add(user)
        db.session.commit()
        return user

    return _make


@pytest.fixture
def admin_user(make_user):
    return make_user('admin_test', rol='admin')


@pytest.fixture
def staff_user(make_user):
    return make_user('recepcionista_test', rol='recepcionista')


@pytest.fixture
def trainer_user(make_user):
    return make_user('entrenador_test', rol='entrenador')


@pytest.fixture
def normal_user(make_user):
    return make_user('usuario_test', rol='usuario')


@pytest.fixture
def admin_client(make_client, admin_user):
    return make_client(admin_user)


@pytest.fixture
def staff_client(make_client, staff_user):
    return make_client(staff_user)


@pytest.fixture
def trainer_client(make_client, trainer_user):
    return make_client(trainer_user)


@pytest.fixture
def user_client(make_client, normal_user):
    return make_client(normal_user)


@pytest.fixture
def plan():
    return _create_plan()


@pytest.fixture
def cliente():
    return _create_cliente()


@pytest.fixture
def horario(trainer_user):
    return _create_horario(trainer_user)


@pytest.fixture
def mock_email(monkeypatch):
    """Captura los correos enviados por auth.forgot_password sin usar SMTP real."""
    emails = []

    def _fake_send_email(destinatario, asunto, cuerpo_html):
        emails.append({
            'to': destinatario,
            'asunto': asunto,
            'cuerpo': cuerpo_html,
        })

    monkeypatch.setattr('app.routes.auth.send_email', _fake_send_email)
    return emails


@pytest.fixture
def plan_factory():
    return _create_plan


@pytest.fixture
def cliente_factory():
    return _create_cliente


@pytest.fixture
def horario_factory():
    return _create_horario


@pytest.fixture
def inscripcion_factory():
    return _create_inscripcion


@pytest.fixture
def pago_factory():
    return _create_pago


@pytest.fixture
def asistencia_cliente_factory():
    return _create_asistencia_cliente


@pytest.fixture
def asistencia_entrenador_factory():
    return _create_asistencia_entrenador


def _create_plan(nombre='Basico', precio=50000.0, duracion=1):
    from app.models.plan import Plan

    plan = Plan(nombrePlan=nombre, precio=precio, duracionMeses=duracion)
    db.session.add(plan)
    db.session.commit()
    return plan


def _create_cliente(nombre='Cliente Uno', edad=25, telefono='3001112233', email=None):
    from app.models.cliente import Cliente

    cliente = Cliente(nombre=nombre, edad=edad, telefono=telefono, email=email)
    db.session.add(cliente)
    db.session.commit()
    return cliente


def _create_horario(trainer, dia='Lunes', inicio='08:00', fin='09:00'):
    from app.models.horario import Horario

    horario = Horario(
        idUser=trainer.idUser,
        dia_semana=dia,
        hora_inicio=inicio,
        hora_fin=fin,
    )
    db.session.add(horario)
    db.session.commit()
    return horario


def _create_inscripcion(cliente, plan):
    from app.models.inscripcion import Inscripcion

    inscripcion = Inscripcion(idCliente=cliente.idCliente, idPlan=plan.idPlan)
    db.session.add(inscripcion)
    db.session.commit()
    return inscripcion


def _create_pago(cliente, monto=50000.0, metodo='Efectivo', inscripcion=None):
    from app.models.pago import Pago

    pago = Pago(
        idCliente=cliente.idCliente,
        idInscripcion=inscripcion.idInscripcion if inscripcion else None,
        monto=monto,
        metodo_pago=metodo,
    )
    db.session.add(pago)
    db.session.commit()
    return pago


def _create_asistencia_cliente(user, con_salida=False):
    from app.models.asistencia_cliente import AsistenciaCliente
    from app.utils import get_colombia_time

    asistencia = AsistenciaCliente(
        idUser=user.idUser,
        fecha=get_colombia_time().date(),
        hora_entrada=get_colombia_time(),
    )
    if con_salida:
        asistencia.hora_salida = get_colombia_time()
    db.session.add(asistencia)
    db.session.commit()
    return asistencia


def _create_asistencia_entrenador(user, horario, con_salida=False):
    from app.models.asistencia import AsistenciaEntrenador
    from app.utils import get_colombia_time

    asistencia = AsistenciaEntrenador(
        idHorario=horario.idHorario,
        idUser=user.idUser,
        fecha=get_colombia_time().date(),
        hora_entrada=get_colombia_time(),
    )
    if con_salida:
        asistencia.hora_salida = get_colombia_time()
    db.session.add(asistencia)
    db.session.commit()
    return asistencia


from app.models.users import User  # noqa: E402  (import al final para evitar ciclos)
