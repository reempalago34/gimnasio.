#!/bin/bash
# Script para iniciar la aplicación Flask con Gunicorn
# Espera a que PostgreSQL esté disponible antes de iniciar

set -e

# Esperar a que PostgreSQL esté disponible
if [ -n "$DATABASE_URL" ]; then
  echo "Esperando a que PostgreSQL esté disponible..."
  
  # Extraer host y puerto del DATABASE_URL
  # Formato esperado: postgresql://usuario:password@host:puerto/bd
  
  DB_HOST=$(echo $DATABASE_URL | sed 's/.*@\([^:]*\).*/\1/')
  DB_PORT=$(echo $DATABASE_URL | sed 's/.*:\([0-9]*\)\/.*/\1/')
  
  # Si no se pudo extraer el puerto, usar el default
  if [ -z "$DB_PORT" ] || [ "$DB_PORT" = "$DATABASE_URL" ]; then
    DB_PORT=5432
  fi
  
  echo "Esperando a $DB_HOST:$DB_PORT..."
  
  # Intentar conectar múltiples veces
  for i in $(seq 1 30); do
    if nc -z $DB_HOST $DB_PORT 2>/dev/null; then
      echo "PostgreSQL está disponible en $DB_HOST:$DB_PORT"
      break
    fi
    echo "Intento $i/30: PostgreSQL no está disponible aún..."
    sleep 1
  done
fi

echo "Iniciando aplicación Flask con Gunicorn..."
exec gunicorn --bind 0.0.0.0:${PORT:-81} \
  --workers 4 \
  --worker-class sync \
  --timeout 60 \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  run:app
