# Usa una imagen oficial de Python liviana
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia e instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el script de Python al contenedor
COPY multicloud_batch_worker.py .

# Comando por defecto para ejecutar el worker
CMD ["python", "multicloud_batch_worker.py"]
