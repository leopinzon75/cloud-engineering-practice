FROM python:3.11-slim
WORKDIR /app

# Install the required cloud libraries inside the container image
RUN pip install --no-cache-dir boto3 azure-storage-blob

COPY multicloud_batch_worker.py .
CMD ["python", "multicloud_batch_worker.py"]
