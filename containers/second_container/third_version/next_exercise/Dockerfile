# Usamos una imagen base oficial de Python ligera basada en Linux Slim
FROM python:3.11-slim

# Establecemos el directorio de trabajo predeterminado dentro del contenedor
WORKDIR /app

# Copiamos el archivo de requerimientos primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalamos las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el script app.py al contenedor
COPY app.py .

# Definimos las variables de entorno para que Python no guarde archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Comando por defecto para arrancar nuestro pipeline de automatización
CMD ["python", "app.py"]
