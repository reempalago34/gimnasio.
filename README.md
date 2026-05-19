# Gimnasio Management System

Este es un sistema de gestión de gimnasio desarrollado con **Flask** y **SQLAlchemy**. Permite la gestión de usuarios, clientes, planes de entrenamiento, inscripciones, pagos y horarios.

## Características

- **Autenticación y Roles**: Manejo de usuarios con roles de Admin, Entrenador, Recepcionista y Usuario.
- **Gestión de Clientes**: Registro y administración de información de clientes.
- **Planes e Inscripciones**: Creación de planes de entrenamiento y seguimiento de inscripciones.
- **Pagos**: Registro de pagos asociados a las inscripciones.
- **Horarios y Asistencia**: Control de horarios para entrenadores y registro de asistencia para clientes.
- **Dashboard**: Panel principal con estadísticas y accesos rápidos según el rol del usuario.
- **Docker Ready**: Incluye configuración Docker para despliegue fácil en Coolify u otros servidores.

## Requisitos

- Python 3.11+
- Flask
- SQLAlchemy
- Flask-Login
- Flask-Migrate (opcional para migraciones)
- python-dotenv (para variables de entorno)
- PostgreSQL (para producción, SQLite para desarrollo local)

## Instalación Local

### Desarrollo con SQLite

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/Gimnasio.git
   cd Gimnasio
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
   Copia `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```
   
   Edita `.env` con tus valores (para desarrollo local, SQLite está bien).

5. Ejecuta la aplicación:
   ```bash
   python run.py
   ```
   
   La aplicación estará disponible en `http://localhost:81`

### Desarrollo con Docker (PostgreSQL)

1. Copia `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edita `.env` con tus valores de PostgreSQL:
   ```env
   DATABASE_URL=postgresql://gimnasio_user:password@db:5432/gimnasio_db
   POSTGRES_USER=gimnasio_user
   POSTGRES_PASSWORD=password
   POSTGRES_DB=gimnasio_db
   SECRET_KEY=tu-clave-secreta
   ```

3. Inicia los contenedores:
   ```bash
   docker-compose up --build
   ```

4. Accede a la aplicación en `http://localhost:81`

## Despliegue en Coolify

Para desplegar en Coolify con PostgreSQL, sigue la guía en [COOLIFY_DEPLOYMENT.md](COOLIFY_DEPLOYMENT.md).

**Resumen rápido:**
1. Conecta tu repositorio a Coolify
2. Configura estas variables de entorno:
   - `DATABASE_URL`: Tu conexión PostgreSQL
   - `SECRET_KEY`: Una clave segura
   - `ADMIN_NAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`: Credenciales del admin inicial
   - `FLASK_ENV`: `production`
3. Coolify construirá y desplegará automáticamente

## Estructura del Proyecto

```
.
├── app/                          # Núcleo de la aplicación
│   ├── __init__.py              # Factory pattern para crear app
│   ├── models/                  # Modelos de base de datos
│   ├── routes/                  # Blueprints de rutas
│   ├── templates/               # Plantillas HTML
│   └── static/                  # Archivos estáticos (CSS, JS, imágenes)
├── instance/                    # Carpeta de instancia (BD local, no en Git)
├── config.py                    # Configuración de la aplicación
├── requirements.txt             # Dependencias Python
├── run.py                       # Punto de entrada
├── Dockerfile                   # Configuración Docker para producción
├── docker-compose.yml           # Orquestación Docker (dev/prod)
└── .env.example                 # Plantilla de variables de entorno
```

## Variables de Entorno

Ver [.env.example](.env.example) para la lista completa de variables requeridas.

**Principales:**
- `DATABASE_URL`: Conexión a la base de datos (PostgreSQL en producción)
- `SECRET_KEY`: Clave secreta de Flask (cambiar en producción)
- `ADMIN_NAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`: Usuario administrador inicial
- `FLASK_ENV`: `development` o `production`
- `PORT`: Puerto de la aplicación (default: 81)

## Notas de Seguridad

- El archivo `.env` **no** debe subirse a repositorios públicos.
- Asegúrate de cambiar `SECRET_KEY` en entornos de producción.
- Usa variables de entorno seguras en Coolify (no incluyas credenciales en el código).
- Para PostgreSQL en producción, usa credenciales fuertes.
- Cambia las credenciales de admin (`ADMIN_PASSWORD`) después del primer despliegue.
