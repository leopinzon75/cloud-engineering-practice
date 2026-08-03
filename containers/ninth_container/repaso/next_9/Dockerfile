FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV SIMULACION=False
ENV AWS_INPUT_BUCKET=dev-fleet-raw-data
ENV AWS_INPUT_KEY=daily_telemetry.csv
ENV AZURE_OUTPUT_CONTAINER=dev-fleet-alerts

CMD ["python", "app.py"]
