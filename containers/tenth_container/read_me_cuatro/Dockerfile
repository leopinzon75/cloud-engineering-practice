# Usa una imagen oficial y ligera de Python
FROM python:3.10-slim

# Evita que Python genere archivos .pyc y fuerza la salida en consola sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define el directorio de trabajo interno
WORKDIR /app

# Copia e instala primero los requerimientos para aprovechar la caché de capas de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código del proyecto al contenedor
COPY . .

# Crea la carpeta de salida para la sincronización del almacenamiento local
RUN mkdir -p output

# Expone el puerto 5000 para el tráfico de la interfaz Flask
EXPOSE 5000

# Comando por defecto para iniciar el servicio web
CMD ["python", "app.py"]
