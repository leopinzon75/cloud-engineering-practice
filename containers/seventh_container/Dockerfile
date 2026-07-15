FROM python:3.11-slim

WORKDIR /app

# Copiamos los requerimientos e instalamos dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el script de integración
COPY app.py .

# Ejecutamos el script por defecto
CMD ["python", "app.py"]
