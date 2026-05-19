-- Script de inicialización de base de datos PostgreSQL para Gimnasio
-- Este script se ejecuta automáticamente en docker-compose con volumes

-- Crear rol/usuario de la aplicación si no existe
DO
$$
BEGIN
  IF NOT EXISTS (
    SELECT FROM pg_roles WHERE rolname = 'Erickgimnasio2026'
  ) THEN
    CREATE ROLE "Erickgimnasio2026" WITH LOGIN PASSWORD 'tu_password_aqui';
    ALTER ROLE "Erickgimnasio2026" CREATEDB;
    GRANT ALL PRIVILEGES ON DATABASE gimnasio_db TO "Erickgimnasio2026";
  END IF;
END
$$;

-- Alternativamente, si usas variables de entorno:
-- CREATE USER IF NOT EXISTS %POSTGRES_USER% WITH PASSWORD '%POSTGRES_PASSWORD%';
-- GRANT ALL PRIVILEGES ON DATABASE %POSTGRES_DB% TO %POSTGRES_USER%;
