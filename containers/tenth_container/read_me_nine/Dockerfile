FROM python:3.10-slim

WORKDIR /app

# Copiamos primero SOLO el requirements.txt
# Esto permite que Docker guarde en cache la instalacion de dependencias
COPY requirements.txt .
RUN pip install --prefer-binary -r requirements.txt

# Copiamos el resto de los archivos despues
COPY app.py .

RUN mkdir -p data/archive/input data/archive/output

CMD ["python", "app.py"]
