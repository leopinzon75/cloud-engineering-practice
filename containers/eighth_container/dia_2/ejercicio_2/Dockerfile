# Usamos una imagen base de Python ligera
FROM python:3.11-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos los requerimientos e instalamos dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos nuestra aplicación
COPY app.py .

# Exponemos el puerto de la app (útil si la corremos como servicio)
EXPOSE 5000

# Comando por defecto
CMD ["python", "app.py"]
