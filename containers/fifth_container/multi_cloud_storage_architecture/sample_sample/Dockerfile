FROM python:3.11-slim
WORKDIR /app

# Instalamos boto3, azure-storage-blob Y AGREGAREMOS moto para el simulador local
RUN pip install --no-cache-dir boto3 azure-storage-blob moto

COPY multicloud_batch_worker.py .
CMD ["python", "multicloud_batch_worker.py"]
