import io
import os
import sys
from pathlib import Path
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

# Entornos y Endpoints
MINIO_ENDPOINT = os.environ.get("AWS_ENDPOINT_URL_S3", "http://localhost:9000").strip()
DYNAMO_ENDPOINT = os.environ.get("AWS_ENDPOINT_URL_DYNAMO", "http://localhost:8000").strip()

S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "fase5-storage-bucket")
S3_KEY = os.environ.get("AWS_INPUT_KEY", "raw_telemetry.csv")
DYNAMO_LOCK_TABLE = "PipelineLockTable"

AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID", "minioadmin")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "minioadmin")

print("🚀 Booting Up Pipeline Engine (MinIO + DynamoDB Lock)...")

# Directorios locales para auditoría
BASE_DIR = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
LOCAL_INPUT_ARCHIVE = BASE_DIR / "data" / "archive" / "input"
LOCAL_OUTPUT_ARCHIVE = BASE_DIR / "data" / "archive" / "output"

LOCAL_INPUT_ARCHIVE.mkdir(parents=True, exist_ok=True)
LOCAL_OUTPUT_ARCHIVE.mkdir(parents=True, exist_ok=True)

# Clientes AWS / Localstack / MinIO
s3 = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    region_name="us-east-1",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url=DYNAMO_ENDPOINT,
    region_name="us-east-1",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

def init_infrastructure():
    """Crea el bucket S3 y la tabla DynamoDB Lock si no existen."""
    try:
        s3.create_bucket(Bucket=S3_BUCKET)
        print(f"📦 [MinIO] Bucket listo: '{S3_BUCKET}'")
    except ClientError as e:
        code = e.response['Error']['Code']
        if code not in ['BucketAlreadyOwnedByYou', 'BucketAlreadyExists']:
            print(f"⚠️ Warning MinIO Bucket: {e}")

    try:
        dynamodb.create_table(
            TableName=DYNAMO_LOCK_TABLE,
            KeySchema=[{'AttributeName': 'LockID', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'LockID', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print(f"⚡ [DynamoDB] Tabla '{DYNAMO_LOCK_TABLE}' creada con éxito.")
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceInUseException':
            print(f"⚠️ Warning DynamoDB Table: {e}")

def acquire_dynamo_lock(lock_id="batch_processing_job"):
    """Adquiere candado exclusivo en DynamoDB."""
    table = dynamodb.Table(DYNAMO_LOCK_TABLE)
    try:
        table.put_item(
            Item={
                'LockID': lock_id,
                'AcquiredAt': datetime.now().isoformat(),
                'Status': 'LOCKED'
            },
            ConditionExpression='attribute_not_exists(LockID)'
        )
        print(f"🔒 [DynamoDB Lock] Candado '{lock_id}' adquirido.")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print(f"⚠️ [DynamoDB Lock] Proceso BLOQUEADO. El candado '{lock_id}' ya está ocupado.")
            return False
        raise e

def release_dynamo_lock(lock_id="batch_processing_job"):
    """Libera el candado en DynamoDB."""
    table = dynamodb.Table(DYNAMO_LOCK_TABLE)
    try:
        table.delete_item(Key={'LockID': lock_id})
        print(f"🔓 [DynamoDB Lock] Candado '{lock_id}' liberado.")
    except Exception as e:
        print(f"❌ Error liberando candado: {e}")

def run_pipeline():
    init_infrastructure()
    
    if not acquire_dynamo_lock():
        sys.exit(0)

    try:
        print("📥 Leyendo datos desde MinIO...")
        try:
            obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
            content = obj['Body'].read().decode('utf-8')
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                print(f"⚠️ Archivo '{S3_KEY}' no existe en MinIO. Generando dataset de prueba (1,000 filas)...")
                header = "timestamp,device_id,temperature,status\n"
                rows = [f"2026-07-31T14:00:00,DEV_{i},{20 + (i % 15)},{'ALERT' if i % 37 == 0 else 'OK'}\n" for i in range(1000)]
                content = header + "".join(rows)
                s3.put_object(Bucket=S3_BUCKET, Key=S3_KEY, Body=content.encode('utf-8'))
            else:
                raise e

        # Procesar alertas
        lines = content.strip().split("\n")
        header = lines[0]
        data_rows = lines[1:]
        
        alerts = [r for r in data_rows if "ALERT" in r]
        print(f"📤 Procesados {len(alerts)} registros de alerta.")

        # Guardar resultados
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"alerts_{timestamp_str}.csv"
        output_content = header + "\n" + "\n".join(alerts)

        # Upload a MinIO
        s3_output_key = f"processed_outputs/{output_filename}"
        s3.put_object(Bucket=S3_BUCKET, Key=s3_output_key, Body=output_content.encode('utf-8'))
        print(f"☁️ [MinIO] Salida subida a: {s3_output_key}")

        # Auditoría Local
        local_output_path = LOCAL_OUTPUT_ARCHIVE / output_filename
        local_output_path.write_text(output_content, encoding="utf-8")
        print(f"💾 [Auditoría Local] Guardado en data/archive/output/")

        print("🏁 ¡Proceso Batch finalizado con éxito!")

    finally:
        release_dynamo_lock()

if __name__ == "__main__":
    run_pipeline()
