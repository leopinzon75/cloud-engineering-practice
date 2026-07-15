FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias en la construcción de la imagen
RUN pip install --no-cache-dir boto3

COPY src/ /app/

CMD ["python", "main.py"]