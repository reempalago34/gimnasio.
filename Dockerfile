# Usar una imagen oficial de Python como base
FROM python:3.11-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg2 y otras librerías
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn psycopg2-binary

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto en el que corre la app (según run.py es el 81)
EXPOSE 81

# Comando para ejecutar la aplicación con Gunicorn en producción
CMD ["gunicorn", "--bind", "0.0.0.0:81", "run:app"]
