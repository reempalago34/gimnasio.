# 🚀 Guía de Despliegue en Coolify

## ¿Qué cambió?

Se han realizado varias mejoras importantes para que funcione correctamente con Docker y Coolify:

1. **app/__init__.py**: Ahora crea las tablas de BD en el primer request (no al boot), esto evita fallos si la BD no está lista.
2. **run.py**: Ya no intenta crear la app al importar, permitiendo que Gunicorn boot correctamente.
3. **Dockerfile**: Incluye un script de startup que espera a que PostgreSQL esté disponible.
4. **docker-compose.yml**: Monta el script de inicialización de BD y tiene mejores healthchecks.
5. **init-db.sql**: Crea automáticamente el usuario de PostgreSQL si no existe.

## Variables de Entorno Requeridas

Debes configurar estas variables de entorno en Coolify:

### Base de Datos PostgreSQL

**Para Coolify (PostgreSQL externo):**
```
DATABASE_URL=postgresql://usuario:contraseña@db.ejemplo.com:5432/gimnasio_db
```

**Estructura de DATABASE_URL:**
```
postgresql://[usuario]:[contraseña]@[host]:[puerto]/[nombre_base_datos]
```

⚠️ **IMPORTANTE**: El host debe ser accesible desde donde está corriendo Coolify. No uses `localhost` o `127.0.0.1`.

### Seguridad
```
SECRET_KEY=tu-clave-secreta-muy-segura-cambiarla-en-produccion
```
Genera una clave segura con:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Credenciales del Admin Inicial
```
ADMIN_NAME=Admin
ADMIN_EMAIL=admin@tudominio.com
ADMIN_PASSWORD=contraseña_segura_aqui
```

### Configuración de la Aplicación
```
FLASK_ENV=production
PORT=81
```

## Pasos para Desplegar en Coolify

1. **Conecta tu repositorio a Coolify**
   - Selecciona el repositorio Git donde está el código

2. **Configura las Variables de Entorno**
   - Ve a "Environment Variables" o "Secrets"
   - Añade todas las variables listadas arriba
   - **CRITICAL**: `DATABASE_URL` debe apuntar a tu PostgreSQL en Coolify u otro servidor

3. **Verifica el Dockerfile**
   - Coolify debería detectarlo automáticamente
   - Si no, especifica: `Dockerfile`

4. **Configura el Puerto (si es necesario)**
   - Por defecto usa puerto 81
   - Si Coolify requiere otro puerto, actualiza en la variable PORT

5. **Deploy**
   - Coolify construirá la imagen Docker y desplegará
   - Espera a que termine (puede tomar algunos minutos)

## Verificación Post-Despliegue

Después de desplegar, verifica que:

1. ✅ Los logs muestren "Esperando a que PostgreSQL esté disponible"
2. ✅ Los logs muestren "Iniciando aplicación Flask con Gunicorn"
3. ✅ Puedes acceder a `/health` (debería retornar `{"status": "healthy"}`)
4. ✅ Puedes acceder al login
5. ✅ El admin inicial se creó (usa las credenciales de ADMIN_EMAIL y ADMIN_PASSWORD)
6. ✅ La base de datos está conectada

## Flujo de Inicialización

```
1. Docker inicia el contenedor
2. Script start.sh espera a que PostgreSQL esté disponible (máx 30 segundos)
3. Gunicorn inicia con 4 workers
4. En el primer request:
   - Flask crea las tablas de BD (si no existen)
   - Flask crea el admin inicial (si no existe)
5. La app está lista para usar
```

## Solución de Problemas

### Error: "could not translate host name"
**Problema**: DATABASE_URL tiene un hostname incorrecto o inaccesible
**Solución**:
- Verifica que el host de PostgreSQL sea correcto
- Asegúrate de que el host sea accesible desde Coolify (no uses localhost)
- Si es PostgreSQL en Coolify, usa el hostname que Coolify proporciona

### Error: "FATAL: role does not exist"
**Problema**: El usuario de PostgreSQL no existe
**Solución**:
- Verifica que POSTGRES_USER y POSTGRES_PASSWORD sean correctos
- Asegúrate de que el usuario existe en PostgreSQL
- Si usas docker-compose, el init-db.sql lo creará automáticamente

### Error: "could not connect to server"
**Problema**: PostgreSQL no está disponible o no responde
**Solución**:
- Espera unos segundos e intenta de nuevo
- Verifica que PostgreSQL esté corriendo
- Verifica la configuración de red (firewall, puertos, etc.)

### La app inicia pero falla al acceder a datos
**Problema**: Las tablas de BD no existen o están corrutas
**Solución**:
- Revisa los logs para "Database initialized successfully"
- Si no aparece, intenta hacer un request a `/health` para disparar la inicialización
- Verifica que el usuario de PostgreSQL tenga permisos de crear tablas

### Admin no se creó
**Problema**: Las credenciales de admin no están configuradas
**Solución**:
- Verifica que ADMIN_EMAIL y ADMIN_PASSWORD estén configuradas
- Revisa los logs para mensajes de error en seed_admin
- Intenta acceder a la app para disparar la creación

## Actualizar Después del Deploy

Si necesitas cambiar variables de entorno:
1. Actualiza en Coolify
2. Redeploy la aplicación

## Base de Datos Persistente

- Coolify mantiene tus datos de PostgreSQL persistentes
- Los datos no se pierden si redespliega la app
- Si usas PostgreSQL administrado (Railway, etc.), los datos están seguros en sus servidores

## Monitoreo

Puedes monitorear el estado con:
- **Health Check**: `GET /health` debería retornar `{"status": "healthy"}`
- **Logs**: Coolify muestra logs en tiempo real
- **Métricas**: Coolify puede monitorear CPU, memoria, etc.
