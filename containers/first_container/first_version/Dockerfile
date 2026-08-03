FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY cloud_pipeline.py .
COPY baseline_test.txt .
CMD ["python", "cloud_pipeline.py"]
