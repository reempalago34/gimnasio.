# Gimnasio Management System

Este es un sistema de gestión de gimnasio desarrollado con **Flask** y **SQLAlchemy**. Permite la gestión de usuarios, clientes, planes de entrenamiento, inscripciones, pagos y horarios.

## Características

- **Autenticación y Roles**: Manejo de usuarios con roles de Admin, Entrenador, Recepcionista y Usuario.
- **Gestión de Clientes**: Registro y administración de información de clientes.
- **Planes e Inscripciones**: Creación de planes de entrenamiento y seguimiento de inscripciones.
- **Pagos**: Registro de pagos asociados a las inscripciones.
- **Horarios y Asistencia**: Control de horarios para entrenadores y registro de asistencia para clientes.
- **Dashboard**: Panel principal con estadísticas y accesos rápidos según el rol del usuario.

## Requisitos

- Python 3.x
- Flask
- SQLAlchemy
- Flask-Login
- Flask-Migrate (opcional para migraciones)
- python-dotenv (para variables de entorno)

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/Gimnasio.git
   ```

2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   # En Windows
   venv\Scripts\activate
   # En Linux/Mac
   source venv/bin/activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura las variables de entorno:
   Crea un archivo `.env` basado en el siguiente ejemplo:
   ```env
   SECRET_KEY=tu_clave_secreta
   DATABASE_URL=sqlite:///flaskdb.sqlite
   ADMIN_NAME=Admin
   ADMIN_EMAIL=admin@example.com
   ADMIN_PASSWORD=admin123
   ```

5. Ejecuta la aplicación:
   ```bash
   python run.py
   ```

## Estructura del Proyecto

- `app/`: Contiene el núcleo de la aplicación (modelos, rutas, plantillas y archivos estáticos).
- `config.py`: Configuración de la aplicación cargando variables desde `.env`.
- `run.py`: Punto de entrada para ejecutar el servidor de desarrollo.
- `requirements.txt`: Lista de dependencias de Python.

## Notas de Seguridad

- El archivo `.env` **no** debe subirse a repositorios públicos.
- Asegúrate de cambiar la `SECRET_KEY` en entornos de producción.
