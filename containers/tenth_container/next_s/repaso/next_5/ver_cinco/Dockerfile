FROM python:3.11-slim

# Evita que Python escriba archivos .pyc y fuerza unbuffering de stdout/stderr para ver logs al instante
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copiar el script de la aplicación
COPY app.py .

# Comando por defecto para iniciar la tarea batch
CMD ["python", "app.py"]
