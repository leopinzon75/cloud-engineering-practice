FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 1. Copiamos el archivo de requerimientos al contenedor
COPY requirements.txt /app/requirements.txt

# 2. Instalamos todas las dependencias listadas en el archivo
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copiamos nuestro código de la API
COPY main.py /app/main.py

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
