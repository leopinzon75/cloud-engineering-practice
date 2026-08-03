FROM python:3.10-slim

WORKDIR /app

# Copiar dependencias e instalarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente y crear estructura de carpetas local
COPY app.py .
RUN mkdir -p data/archive/input data/archive/output

# Crear un usuario sin privilegios por seguridad
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python", "app.py"]
