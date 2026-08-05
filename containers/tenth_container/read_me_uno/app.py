import io
import os
import sys
from pathlib import Path
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from moto import mock_aws

# Detectar si estamos usando mock en memoria o endpoints reales
USE_MOCK = os.environ.get("USE_MOCK", "true").lower() == "true"

MINIO_ENDPOINT = None if USE_MOCK else os.environ.get("AWS_ENDPOINT_URL_S3", "http://localhost:9000").strip()
DYNAMO_ENDPOINT = None if USE_MOCK else os.environ.get("AWS_ENDPOINT_URL_DYNAMO", "http://localhost:8000").strip()

S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "fase5-storage-bucket")
S3_KEY = os.environ.get("AWS_INPUT_KEY", "raw_telemetry.csv")
DYNAMO_LOCK_TABLE = "PipelineLockTable"

AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID", "minioadmin")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "minioadmin")

# Directorios locales para auditoría
BASE_DIR = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
LOCAL_INPUT_ARCHIVE = BASE_DIR / "data" / "archive" / "input"
LOCAL_OUTPUT_ARCHIVE = BASE_DIR / "data" / "archive" / "output"

LOCAL_INPUT_ARCHIVE.mkdir(parents=True, exist_ok=True)
LOCAL_OUTPUT_ARCHIVE.mkdir(parents=True, exist_ok=True)

def get_clients():
    """Inicializa los clientes boto3 ajustando endpoint_url según el entorno."""
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
    return s3, dynamodb

def init_infrastructure(s3, dynamodb):
    try:
        s3.create_bucket(Bucket=S3_BUCKET)
        print(f"📦 [S3/MinIO] Bucket listo: '{S3_BUCKET}'")
    except ClientError as e:
        code = e.response['Error']['Code']
        if code not in ['BucketAlreadyOwnedByYou', 'BucketAlreadyExists']:
            print(f"⚠️ Warning Bucket: {e}")

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

def acquire_dynamo_lock(dynamodb, lock_id="batch_processing_job"):
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

def release_dynamo_lock(dynamodb, lock_id="batch_processing_job"):
    table = dynamodb.Table(DYNAMO_LOCK_TABLE)
    try:
        table.delete_item(Key={'LockID': lock_id})
        print(f"🔓 [DynamoDB Lock] Candado '{lock_id}' liberado.")
    except Exception as e:
        print(f"❌ Error liberando candado: {e}")

def run_pipeline():
    s3, dynamodb = get_clients()
    init_infrastructure(s3, dynamodb)

    if not acquire_dynamo_lock(dynamodb):
        sys.exit(0)

    try:
        print("📥 Leyendo datos desde S3/MinIO...")
        try:
            obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
            content = obj['Body'].read().decode('utf-8')
        except ClientError as e:
            if e.response['Error']['Code'] in ['NoSuchKey', '404']:
                print(f"⚠️ Archivo '{S3_KEY}' no existe. Generando dataset de prueba (1,000 filas)...")
                header = "timestamp,device_id,temperature,status\n"
                rows = [f"2026-07-31T14:00:00,DEV_{i},{20 + (i % 15)},{'ALERT' if i % 37 == 0 else 'OK'}\n" for i in range(1000)]
                content = header + "".join(rows)
                s3.put_object(Bucket=S3_BUCKET, Key=S3_KEY, Body=content.encode('utf-8'))
            else:
                raise e

        lines = content.strip().split("\n")
        header = lines[0]
        data_rows = lines[1:]

        alerts = [r for r in data_rows if "ALERT" in r]
        print(f"📤 Procesados {len(alerts)} registros de alerta.")

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"alerts_{timestamp_str}.csv"
        output_content = header + "\n" + "\n".join(alerts)

        s3_output_key = f"processed_outputs/{output_filename}"
        s3.put_object(Bucket=S3_BUCKET, Key=s3_output_key, Body=output_content.encode('utf-8'))
        print(f"☁️ [S3/MinIO] Salida subida a: {s3_output_key}")

        local_output_path = LOCAL_OUTPUT_ARCHIVE / output_filename
        local_output_path.write_text(output_content, encoding="utf-8")
        print(f"💾 [Auditoría Local] Guardado en {local_output_path}")

        print("🏁 ¡Proceso Batch finalizado con éxito!")

    finally:
        release_dynamo_lock(dynamodb)

@mock_aws
def main():
    print("🚀 Booting Up Pipeline Engine (In-Memory Mock AWS)...")
    run_pipeline()

if __name__ == "__main__":
    main()
import io
import os
import sys
from pathlib import Path
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from moto import mock_aws

# Detectar si estamos usando mock en memoria o endpoints reales
USE_MOCK = os.environ.get("USE_MOCK", "true").lower() == "true"

MINIO_ENDPOINT = None if USE_MOCK else os.environ.get("AWS_ENDPOINT_URL_S3", "http://localhost:9000").strip()
DYNAMO_ENDPOINT = None if USE_MOCK else os.environ.get("AWS_ENDPOINT_URL_DYNAMO", "http://localhost:8000").strip()

S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "fase5-storage-bucket")
S3_KEY = os.environ.get("AWS_INPUT_KEY", "raw_telemetry.csv")
DYNAMO_LOCK_TABLE = "PipelineLockTable"

AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID", "minioadmin")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "minioadmin")

# Directorios locales para auditoría
BASE_DIR = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
LOCAL_INPUT_ARCHIVE = BASE_DIR / "data" / "archive" / "input"
LOCAL_OUTPUT_ARCHIVE = BASE_DIR / "data" / "archive" / "output"

LOCAL_INPUT_ARCHIVE.mkdir(parents=True, exist_ok=True)
LOCAL_OUTPUT_ARCHIVE.mkdir(parents=True, exist_ok=True)

def get_clients():
    """Inicializa los clientes boto3 ajustando endpoint_url según el entorno."""
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
    return s3, dynamodb

def init_infrastructure(s3, dynamodb):
    try:
        s3.create_bucket(Bucket=S3_BUCKET)
        print(f"📦 [S3/MinIO] Bucket listo: '{S3_BUCKET}'")
    except ClientError as e:
        code = e.response['Error']['Code']
        if code not in ['BucketAlreadyOwnedByYou', 'BucketAlreadyExists']:
            print(f"⚠️ Warning Bucket: {e}")

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

def acquire_dynamo_lock(dynamodb, lock_id="batch_processing_job"):
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

def release_dynamo_lock(dynamodb, lock_id="batch_processing_job"):
    table = dynamodb.Table(DYNAMO_LOCK_TABLE)
    try:
        table.delete_item(Key={'LockID': lock_id})
        print(f"🔓 [DynamoDB Lock] Candado '{lock_id}' liberado.")
    except Exception as e:
        print(f"❌ Error liberando candado: {e}")

def run_pipeline():
    s3, dynamodb = get_clients()
    init_infrastructure(s3, dynamodb)

    if not acquire_dynamo_lock(dynamodb):
        sys.exit(0)

    try:
        print("📥 Leyendo datos desde S3/MinIO...")
        try:
            obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
            content = obj['Body'].read().decode('utf-8')
        except ClientError as e:
            if e.response['Error']['Code'] in ['NoSuchKey', '404']:
                print(f"⚠️ Archivo '{S3_KEY}' no existe. Generando dataset de prueba (1,000 filas)...")
                header = "timestamp,device_id,temperature,status\n"
                rows = [f"2026-07-31T14:00:00,DEV_{i},{20 + (i % 15)},{'ALERT' if i % 37 == 0 else 'OK'}\n" for i in range(1000)]
                content = header + "".join(rows)
                s3.put_object(Bucket=S3_BUCKET, Key=S3_KEY, Body=content.encode('utf-8'))
            else:
                raise e

        lines = content.strip().split("\n")
        header = lines[0]
        data_rows = lines[1:]

        alerts = [r for r in data_rows if "ALERT" in r]
        print(f"📤 Procesados {len(alerts)} registros de alerta.")

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"alerts_{timestamp_str}.csv"
        output_content = header + "\n" + "\n".join(alerts)

        s3_output_key = f"processed_outputs/{output_filename}"
        s3.put_object(Bucket=S3_BUCKET, Key=s3_output_key, Body=output_content.encode('utf-8'))
        print(f"☁️ [S3/MinIO] Salida subida a: {s3_output_key}")

        local_output_path = LOCAL_OUTPUT_ARCHIVE / output_filename
        local_output_path.write_text(output_content, encoding="utf-8")
        print(f"💾 [Auditoría Local] Guardado en {local_output_path}")

        print("🏁 ¡Proceso Batch finalizado con éxito!")

    finally:
        release_dynamo_lock(dynamodb)

@mock_aws
def main():
    print("🚀 Booting Up Pipeline Engine (In-Memory Mock AWS)...")
    run_pipeline()

if __name__ == "__main__":
    main()
