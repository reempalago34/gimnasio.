# Usar una imagen oficial de Python como base
FROM python:3.11-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Variables de compilación
ARG PORT=81
ENV PORT=${PORT}

# Instalar dependencias del sistema necesarias para psycopg2 y otras librerías
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn psycopg2-binary

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto dinámico
EXPOSE ${PORT}

# Comando para ejecutar la aplicación con Gunicorn en producción
# El puerto se puede pasar como variable de entorno
CMD gunicorn --bind 0.0.0.0:${PORT} --workers 4 --worker-class sync --timeout 60 --access-logfile - --error-logfile - run:app
