# 🚀 Guía de Despliegue en Coolify

## Variables de Entorno Requeridas

Debes configurar estas variables de entorno en Coolify:

### Base de Datos PostgreSQL
```
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/nombre_base_datos
```

**Ejemplo:**
```
DATABASE_URL=postgresql://gimnasio:mypassword@db.railway.app:5432/gimnasio_db
```

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
   - **IMPORTANTE:** DATABASE_URL debe apuntar a tu PostgreSQL en Coolify

3. **Selecciona el Dockerfile**
   - Coolify debería detectarlo automáticamente
   - Si no, especifica: `Dockerfile`

4. **Configura el Puerto (si es necesario)**
   - Por defecto usa puerto 81
   - Si Coolify requiere otro puerto, actualiza en la variable PORT

5. **Deploy**
   - Coolify construccionará la imagen Docker y desplegará

## Verificación Post-Despliegue

Después de desplegar, verifica que:

1. ✅ La aplicación inicia sin errores
2. ✅ Puedes acceder al login
3. ✅ El admin inicial se creó (usa las credenciales de ADMIN_EMAIL y ADMIN_PASSWORD)
4. ✅ La base de datos está conectada (puedes acceder a secciones que usan BD)

## Solución de Problemas

### Error: "could not translate host name"
- Verifica que DATABASE_URL sea correcto
- Asegúrate de que el host de PostgreSQL sea accesible desde Coolify

### Error: "psycopg2 connection failed"
- Verifica las credenciales en DATABASE_URL
- Verifica que PostgreSQL esté corriendo

### Error: "module not found"
- Los requisitos (requirements.txt) deberían instalarse automáticamente
- Si no, comprueba que no hay dependencias faltantes

### El admin no se creó
- Verifica ADMIN_EMAIL y ADMIN_PASSWORD
- Revisa los logs de Coolify para mensajes de error

## Actualizar Variables Después del Deploy

Si necesitas cambiar variables de entorno:
1. Actualiza en Coolify
2. Redeploy la aplicación

## Base de Datos Persistente

Coolify mantendrá tus datos de PostgreSQL persistentes. Los datos no se pierden si redespliega la app.
