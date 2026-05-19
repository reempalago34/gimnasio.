from app import create_app, db

# Crear la app sin ejecutarla inmediatamente
app = create_app()

if __name__ == '__main__':
    # Solo se ejecuta en desarrollo local, nunca con Gunicorn
    with app.app_context():
        db.create_all()
    app.run(debug=False, host='0.0.0.0', port=81)