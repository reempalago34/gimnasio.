# Usar una imagen oficial de Python como base
FROM python:3.11-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Variables de compilación
ARG PORT=81
ENV PORT=${PORT}

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libzbar0 \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requerimientos e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn psycopg2-binary

# Copiar el resto del código de la aplicación con permisos de ejecución para start.sh
COPY --chmod=755 . .

# Dar permisos adicionales al script start.sh
RUN chmod +x /app/start.sh && ls -la /app/start.sh

# Exponer el puerto dinámico
EXPOSE ${PORT}

# Health check para Docker/Coolify
HEALTHCHECK --interval=30s --timeout=10s --start-period=45s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Comando para ejecutar la aplicación usando /bin/bash
CMD ["/bin/bash", "/app/start.sh"]
