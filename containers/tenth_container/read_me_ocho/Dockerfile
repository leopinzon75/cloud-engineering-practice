FROM python:3.10-slim

WORKDIR /app

# Actualizamos pip e instalamos dependencias usando binarios precompilados
COPY requirements.txt .
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Copiamos el archivo de la aplicación
COPY app.py .

CMD ["python", "app.py"]
