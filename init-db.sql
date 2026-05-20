-- Script de inicialización de base de datos PostgreSQL para Gimnasio
-- Este script se ejecuta automáticamente en docker-compose
-- Las variables de entorno (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB) 
-- son configuradas automáticamente por PostgreSQL al iniciar el contenedor

-- Nota: PostgreSQL crea automáticamente:
-- 1. El usuario con el nombre en POSTGRES_USER
-- 2. La base de datos con el nombre en POSTGRES_DB
-- Este archivo es principalmente para migraciones o datos iniciales personalizados

-- Si necesitas agregar datos iniciales, hazlo aquí:
-- INSERT INTO ... VALUES (...);

-- Verificación: Mostrar que la base de datos fue creada correctamente
SELECT 'Base de datos inicializada correctamente' as status;
