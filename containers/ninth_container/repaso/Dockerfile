FROM python:3.10-slim

WORKDIR /app

# Copiar requerimientos e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente y tests
COPY . .

# Comando por defecto al ejecutar el contenedor
CMD ["python", "app.py"]
