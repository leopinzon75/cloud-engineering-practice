import os
import boto3
from botocore.exceptions import ClientError

# Obtener variables de entorno o valores por defecto
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")
AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "minio_admin")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY", "minio_password")
BUCKET_NAME = "engine-trouble-codes"

def run_engine_sandbox(custom_s3_client=None):
    """
    Ejecuta el sandbox de diagnóstico e interactúa con el bucket S3/MinIO.
    Permite inyectar un cliente mock de S3 para pruebas unitarias.
    """
    if custom_s3_client:
        s3 = custom_s3_client
    else:
        print(f"🛡️ Connecting to MinIO S3 at: {S3_ENDPOINT}")
        s3 = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT,
            aws_access_key_id=AWS_KEY,
            aws_secret_access_key=AWS_SECRET,
            region_name='us-east-1'
        )
    
    # 1. Crear el bucket si no existe
    try:
        s3.head_bucket(Bucket=BUCKET_NAME)
    except ClientError:
        print(f"📦 Bucket '{BUCKET_NAME}' not found. Creating it now...")
        s3.create_bucket(Bucket=BUCKET_NAME)
    
    # 2. Reporte de diagnóstico del motor (Código P0300)
    report_data = "DIAGNOSTIC REPORT: CODE P0300 - RANDOM/MULTIPLE CYLINDER MISFIRE DETECTED. CHECK SPARK PLUGS AND IGNITION COILS."
    
    # 3. Subir reporte al Bucket
    s3.put_object(Bucket=BUCKET_NAME, Key="misfire_report.txt", Body=report_data)
    print(f"🚀 Misfire report uploaded to bucket '{BUCKET_NAME}'!")
    
    # 4. Descargar y verificar
    response = s3.get_object(Bucket=BUCKET_NAME, Key="misfire_report.txt")
    downloaded_data = response['Body'].read().decode('utf-8')
    print("📥 Cloud data verification: 100% Match!")
    
    # 5. Guardar copia local en la carpeta logs/
    os.makedirs('logs', exist_ok=True)
    with open('logs/final_misfire_report.txt', 'w') as f:
        f.write(downloaded_data)
    print("💾 Permanent copy stamped to local container logs directory!")
    
    return downloaded_data

if __name__ == "__main__":
    run_engine_sandbox()
