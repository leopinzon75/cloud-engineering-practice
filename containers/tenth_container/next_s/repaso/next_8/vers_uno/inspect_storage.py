import os
import boto3
from azure.storage.blob import BlobServiceClient

# ---------------------------------------------------------
# Configuración con el nuevo puerto de MinIO (9010)
# ---------------------------------------------------------
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

def inspect_minio_s3():
    print("==================================================")
    print("  🔍 INSPECCIONANDO ALMACENAMIENTO: MinIO (Port 9010)")
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
        print(f"📌 Buckets detectados en MinIO: {buckets}")

        if S3_BUCKET in buckets:
            print(f"✅ Bucket '{S3_BUCKET}' encontrado. Listando contenido...")
            response = s3_client.list_objects_v2(Bucket=S3_BUCKET)

            if "Contents" in response:
                for obj in response["Contents"]:
                    print(f"   📄 Objeto: {obj['Key']} | Tamaño: {obj['Size']} bytes | Úl. Modificación: {obj['LastModified']}")
            else:
                print(f"   ⚠️  El bucket '{S3_BUCKET}' existe pero está vacío.")
        else:
            print(f"❌ El bucket '{S3_BUCKET}' no existe aún en MinIO.")

    except Exception as e:
        print(f"❌ Error al conectar o consultar MinIO: {e}")

def inspect_azure():
    print("\n==================================================")
    print("  🔍 INSPECCIONANDO ALMACENAMIENTO: AZURE BLOB")
    print("==================================================")
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        containers = [c.name for c in blob_service_client.list_containers()]
        print(f"📌 Contenedores detectados en Azure: {containers}")

        if AZURE_CONTAINER in containers:
            print(f"✅ Contenedor '{AZURE_CONTAINER}' encontrado. Listando blobs...")
            container_client = blob_service_client.get_container_client(AZURE_CONTAINER)
            blobs = list(container_client.list_blobs())

            if blobs:
                for blob in blobs:
                    print(f"   📦 Blob: {blob.name} | Tamaño: {blob.size} bytes | Tipo: {blob.blob_type}")
            else:
                print(f"   ⚠️  El contenedor '{AZURE_CONTAINER}' existe pero está vacío.")
        else:
            print(f"❌ El contenedor '{AZURE_CONTAINER}' no existe aún en Azure Blob Storage.")

    except Exception as e:
        print(f"❌ Error al conectar o consultar Azure Blob Storage: {e}")

if __name__ == "__main__":
    inspect_minio_s3()
    inspect_azure()
