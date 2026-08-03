FROM python:3.11-slim

WORKDIR /app

# Copiar dependencias e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el script de la aplicación
COPY app.py .

# Comando por defecto al arrancar el contenedor
CMD ["python", "app.py"]
