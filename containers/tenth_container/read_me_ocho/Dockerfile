FROM python:3.11-slim

WORKDIR /app

# Copiamos el archivo de dependencias e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente de la aplicación
COPY app.py .

# Comando por defecto al levantar el contenedor
CMD ["python", "app.py"]
