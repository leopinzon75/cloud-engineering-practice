import boto3
from botocore.exceptions import EndpointConnectionError

print("🚀 Booting up Multi-Cloud Pipeline (Fase 6 Test)...")
print("🔗 Conectando al Endpoint: http://localstack-bridge:4566")

try:
    s3 = boto3.client(
        's3',
        endpoint_url='http://localstack-bridge:4566',
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name='us-east-1'
    )
    response = s3.list_buckets()
    print("✅ Conexión exitosa a LocalStack!")
    print("📊 Buckets disponibles:", response.get('Buckets', []))
except EndpointConnectionError as e:
    print("❌ Error: No se pudo conectar a LocalStack.", e)
except Exception as e:
    print("⚠️ Ocurrió un error inesperado:", e)
