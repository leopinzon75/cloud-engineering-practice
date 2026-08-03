# Base ligera oficial de Python
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar requerimientos primero para optimizar la caché de capas de Docker
COPY requirements.txt .

# Instalar las librerías de AWS y Azure
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el script de telemetría que estampamos antes
COPY multicloud_batch_worker.py .

# Crear el punto de montaje para persistir los archivos en tu Mac
VOLUME /app/data

# Comando para ejecutar el pipeline
CMD ["python", "multicloud_batch_worker.py"]
