import os
import time
import pandas as pd
import numpy as np
import boto3
from azure.storage.blob import BlobServiceClient

# Configuración por variables de entorno
MINIO_ENDPOINT_URL = os.getenv("MINIO_ENDPOINT_URL", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
S3_BUCKET = os.getenv("S3_BUCKET", "fleet-raw-data")

AZURE_CONNECTION_STRING = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING",
    "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://azurite:10000/devstoreaccount1;"
)
AZURE_CONTAINER = os.getenv("AZURE_CONTAINER", "fleet-clean-alerts")
INTERVAL_SECONDS = int(os.getenv("SIMULATION_INTERVAL", "15"))

def generate_telemetry_batch():
    df = pd.DataFrame({
        "device_id": [f"TRUCK-{i:03d}" for i in range(1, 21)],
        "speed": np.random.uniform(50, 115, 20),
        "engine_temp": np.random.uniform(85, 110, 20),
        "timestamp": pd.date_range(end=pd.Timestamp.now(), periods=20, freq='s')
    })
    return df

def run_orchestrator():
    print("🚀 Iniciando simulador continuo Multi-Cloud Fleet (MinIO + Azure)...")
    
    # Inicializar cliente S3 (MinIO)
    s3_client = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT_URL,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name="us-east-1"
    )
    
    # Inicializar cliente Azure Blob
    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_CONNECTION_STRING,
        api_version="2023-11-03"
    )

    batch_id = 1
    while True:
        try:
            print(f"\n--- [Lote #{batch_id}] Generando telemetría en tiempo real ---")
            df = generate_telemetry_batch()
            csv_data = df.to_csv(index=False)
            
            # 1. Enviar a MinIO
            s3_key = f"telemetry_batch_{batch_id}.csv"
            s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=csv_data)
            print(f"✅ S3/MinIO: Subido '{s3_key}' al bucket '{S3_BUCKET}'")

            # 2. Filtrar Alertas y Enviar a Azure
            df_alerts = df[(df['speed'] > 100) | (df['engine_temp'] > 105)]
            if not df_alerts.empty:
                azure_blob = f"alerts_batch_{batch_id}.csv"
                container_client = blob_service_client.get_container_client(AZURE_CONTAINER)
                container_client.upload_blob(name=azure_blob, data=df_alerts.to_csv(index=False), overwrite=True)
                print(f"⚠️ Azure Blob: Subidas {len(df_alerts)} alertas a '{AZURE_CONTAINER}/{azure_blob}'")
            else:
                print("ℹ️ Azure Blob: No se detectaron alertas en este lote.")

            batch_id += 1
            time.sleep(INTERVAL_SECONDS)

        except Exception as e:
            print(f"❌ Error durante el ciclo de simulación: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_orchestrator()
