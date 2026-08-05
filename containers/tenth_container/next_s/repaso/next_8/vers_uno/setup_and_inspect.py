import os
import boto3
from azure.storage.blob import BlobServiceClient

MINIO_ENDPOINT_URL = os.getenv("MINIO_ENDPOINT_URL", "http://localhost:9010")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
S3_BUCKET = "fleet-raw-data"

AZURE_CONNECTION_STRING = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING",
    "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)
AZURE_CONTAINER = "fleet-clean-alerts"
LOCAL_FILE_PATH = os.path.join("fleet_data", "raw_fleet_telemetry.csv")

def setup_and_inspect_minio():
    print("==================================================")
    print("  🚀 PROCESANDO ALMACENAMIENTO: MinIO (Port 9010)")
    print("==================================================")
    try:
        s3_client = boto3.client(
            "s3",
            endpoint_url=MINIO_ENDPOINT_URL,
            aws_access_key_id=MINIO_ACCESS_KEY,
            aws_secret_access_key=MINIO_SECRET_KEY,
            region_name="us-east-1"
        )

        buckets = [b["Name"] for b in s3_client.list_buckets().get("Buckets", [])]
        if S3_BUCKET not in buckets:
            print(f"⚙️ Creando el bucket '{S3_BUCKET}' en MinIO...")
            s3_client.create_bucket(Bucket=S3_BUCKET)
            print(f"✅ Bucket '{S3_BUCKET}' creado exitosamente.")
        else:
            print(f"📌 Bucket '{S3_BUCKET}' ya existe.")

        if os.path.exists(LOCAL_FILE_PATH):
            s3_key = "raw_telemetry.csv"
            print(f"📤 Subiendo '{LOCAL_FILE_PATH}' a MinIO como '{s3_key}'...")
            s3_client.upload_file(LOCAL_FILE_PATH, S3_BUCKET, s3_key)
            print("✅ Carga en MinIO completada.")

        response = s3_client.list_objects_v2(Bucket=S3_BUCKET)
        print("\n📄 Contenido del Bucket MinIO:")
        if "Contents" in response:
            for obj in response["Contents"]:
                print(f"   └─ Objeto: {obj['Key']} | Tamaño: {obj['Size']} bytes")
        else:
            print("   └─ El bucket está vacío.")

    except Exception as e:
        print(f"❌ Error en MinIO: {e}")

def setup_and_inspect_azure():
    print("\n==================================================")
    print("  🚀 PROCESANDO ALMACENAMIENTO: AZURE BLOB")
    print("==================================================")
    try:
        # Se fuerza api_version compatible con Azurite
        blob_service_client = BlobServiceClient.from_connection_string(
            AZURE_CONNECTION_STRING,
            api_version="2023-11-03"
        )

        containers = [c.name for c in blob_service_client.list_containers()]
        if AZURE_CONTAINER not in containers:
            print(f"⚙️ Creando el contenedor '{AZURE_CONTAINER}' en Azure...")
            container_client = blob_service_client.create_container(AZURE_CONTAINER)
            print(f"✅ Contenedor '{AZURE_CONTAINER}' creado exitosamente.")
        else:
            print(f"📌 Contenedor '{AZURE_CONTAINER}' ya existe.")
            container_client = blob_service_client.get_container_client(AZURE_CONTAINER)

        if os.path.exists(LOCAL_FILE_PATH):
            blob_name = "clean_telemetry.csv"
            print(f"📤 Subiendo '{LOCAL_FILE_PATH}' a Azure como '{blob_name}'...")
            with open(LOCAL_FILE_PATH, "rb") as data:
                container_client.upload_blob(name=blob_name, data=data, overwrite=True)
            print("✅ Carga en Azure Blob completada.")

        blobs = list(container_client.list_blobs())
        print("\n📦 Contenido del Contenedor Azure:")
        if blobs:
            for blob in blobs:
                print(f"   └─ Blob: {blob.name} | Tamaño: {blob.size} bytes")
        else:
            print("   └─ El contenedor está vacío.")

    except Exception as e:
        print(f"❌ Error en Azure Blob: {e}")

if __name__ == "__main__":
    setup_and_inspect_minio()
    setup_and_inspect_azure()
