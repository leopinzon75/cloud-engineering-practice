import boto3
from botocore.exceptions import ClientError
import time

# Configuración del endpoint local
LOCALSTACK_ENDPOINT = "http://127.0.0.1:4566"
TABLE_NAME = "fase5-execution-locks"

print("🔄 Conectando con el servicio DynamoDB en LocalStack...")
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=LOCALSTACK_ENDPOINT,
    region_name='us-east-1',
    aws_access_key_id='mock_key',
    aws_secret_access_key='mock_secret'
)

table = dynamodb.Table(TABLE_NAME)

def probar_ciclo_bloqueo():
    lock_id = f"batch_run_{int(time.time())}"
    
    # 1. Intentar adquirir el Lock
    print(f"📥 Intentando adquirir bloqueo con ID: {lock_id}...")
    try:
        table.put_item(
            Item={
                'LockID': lock_id,
                'Status': 'PROCESSING',
                'Timestamp': str(time.time())
            },
            # Esta condición asegura que el bloqueo falle si el ID ya existe
            ConditionExpression='attribute_not_exists(LockID)'
        )
        print("✅ ¡Bloqueo ADQUIRIDO con éxito en DynamoDB!")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print("❌ Error: El bloqueo ya existe.")
        else:
            print(f"❌ Error inesperado al adquirir: {e}")
        return

    # Espera simulada de procesamiento corta
    time.sleep(2)

    # 2. Intentar liberar el Lock
    print(f"📤 Intentando liberar el bloqueo: {lock_id}...")
    try:
        table.delete_item(
            Key={'LockID': lock_id}
        )
        print("✅ ¡Bloqueo LIBERADO con éxito! La tabla quedó limpia.")
    except ClientError as e:
        print(f"❌ Error al liberar el bloqueo: {e}")

if __name__ == "__main__":
    try:
        # Verificar primero si la tabla existe
        table.load()
        print(f"📊 Tabla '{TABLE_NAME}' detectada correctamente.")
        probar_ciclo_bloqueo()
    except ClientError as e:
        print(f"❌ No se pudo acceder a la tabla. ¿Corriste Terraform? Detalles: {e}")
