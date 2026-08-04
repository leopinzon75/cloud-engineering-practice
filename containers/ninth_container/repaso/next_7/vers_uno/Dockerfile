FROM python:3.11-slim

# Evita la generación de archivos .pyc y fuerza stdout/stderr sin buffer
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copiamos e instalamos dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente
COPY app.py .

# Creamos las estructuras de carpetas necesarias
RUN mkdir -p data/input data/output

CMD ["python", "app.py"]
