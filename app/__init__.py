from flask import Flask, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

# Variable para rastrear si las tablas ya fueron creadas
_db_initialized = False

def create_app():
    global _db_initialized
    
    app = Flask(__name__)    
    app.config.from_object('config.Config')
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Import models so SQLAlchemy metadata includes them
    from app.models.users import User
    from app.models.cliente import Cliente
    from app.models.plan import Plan
    from app.models.inscripcion import Inscripcion
    from app.models.horario import Horario
    from app.models.pago import Pago
    from app.models.asistencia import AsistenciaEntrenador
    from app.models.asistencia_cliente import AsistenciaCliente

    @login_manager.user_loader
    def load_user(idUser):
        return User.query.get(int(idUser))

    # Inicializar BD en el primer request para evitar errores de conexión
    @app.before_request
    def init_db():
        global _db_initialized
        if not _db_initialized:
            try:
                with app.app_context():
                    db.create_all()
                    seed_admin(app)
                    _db_initialized = True
                    print("Database initialized successfully")
            except Exception as e:
                # Log el error pero no falla la app
                print(f"Warning: Could not initialize database on first request: {str(e)}")
                # Intenta de nuevo en el siguiente request

    # Register blueprints
    from app.routes import (
        auth, users_route,
        users_route_async,
        cliente_routes, plan_routes, inscripcion_routes, horario_routes, pago_routes
    )
    app.register_blueprint(auth.bp)
    app.register_blueprint(users_route.bp)
    app.register_blueprint(users_route_async.bp)
    app.register_blueprint(cliente_routes.bp)
    app.register_blueprint(plan_routes.bp)
    app.register_blueprint(inscripcion_routes.bp)
    app.register_blueprint(horario_routes.bp)
    app.register_blueprint(pago_routes.bp)

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, 'static'),
            'favicon.ico', mimetype='image/x-icon'
        )

    @app.route('/health')
    def health():
        """Health check endpoint para Coolify/Docker"""
        try:
            # Intenta hacer una query simple para verificar la BD
            db.session.execute(db.text('SELECT 1'))
            return {'status': 'healthy'}, 200
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}, 503

    @app.errorhandler(404)
    def not_found(e):
        # Si la ruta no existe, redirigir al login
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))

    @app.errorhandler(Exception)
    def handle_error(e):
        print(f"An error occurred: {str(e)}")
        return {"error": str(e)}, 500

    return app

def seed_admin(app):
    from app.models.users import User
    admin_email = app.config.get('ADMIN_EMAIL')
    admin_name = app.config.get('ADMIN_NAME')
    admin_password = app.config.get('ADMIN_PASSWORD')
    
    if not admin_email or not admin_password:
        return

    try:
        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            admin_user = User(
                nombre=admin_name,
                email=admin_email,
                passwordUser=admin_password,
                rol='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"Admin user {admin_email} created successfully.")
    except Exception as e:
        print(f"Warning: Could not seed admin user: {str(e)}")
        db.session.rollback()