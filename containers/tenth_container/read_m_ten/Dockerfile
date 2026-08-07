FROM python:3.10-slim

WORKDIR /app

# Copia de dependencias optimizada para caché
COPY requirements.txt .
RUN pip install --prefer-binary -r requirements.txt

# Copia del script de la aplicación
COPY app.py .

# Creación preventiva de directorios de auditoría
RUN mkdir -p data/archive/input data/archive/output

CMD ["python", "app.py"]
