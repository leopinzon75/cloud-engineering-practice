FROM python:3.10-slim

WORKDIR /app

# Copiar dependencias
RUN pip install --no-cache-dir flask boto3

# Copiar el código
COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
