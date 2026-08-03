FROM python:3.11-slim

WORKDIR /app

# Copiar e instalar dependencias directamente
RUN pip install --no-cache-dir flask boto3

# Copiar el código fuente
COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
