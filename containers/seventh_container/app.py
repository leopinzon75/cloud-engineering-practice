import io
import os
import time
import socket
from pathlib import Path
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

# =========================================================
# CONFIGURACIÓN DINÁMICA E INFRAESTRUCTURA LOCALSTACK
# =========================================================
SIMULATION_ENV = os.environ.get("SIMULACION", "True")
SIMULATION_MODE = SIMULATION_ENV.upper() == "TRUE"

# Enlaces directos a las variables del docker-compose
AWS_ENDPOINT = os.environ.get("AWS_ENDPOINT_URL", "http://localstack_simulador:4566").strip()
AWS_BUCKET = os.environ.get("S3_BUCKET_NAME", "fase5-storage-bucket")
AWS_KEY = os.environ.get("AWS_INPUT_KEY", "raw_telemetry.csv")
LOCK_TABLE = os.environ.get("DYNAMODB_LOCK_TABLE", "fase5-execution-locks")

print(f"🚀 Live Enterprise Multi-Cloud Pipeline Booting Up...")
print(f"🎛️  Modo de Simulación: {'ACTIVADO (3 filas en memoria)' if SIMULATION_MODE else 'DESACTIVADO (1,000 filas reales en LocalStack S3)'}")

BASE_DIR = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
LOCAL_INPUT_ARCHIVE = BASE_DIR / "data" / "archive" / "input"
LOCAL_OUTPUT_ARCHIVE = BASE_DIR / "data" / "archive" / "output"

# =========================================================
# GESTIÓN DE CANDADOS DISTRIBUIDOS (DynamoDB - Sin SQS)
# =========================================================
def acquire_lock(dynamodb_client, lock_id, ttl_seconds=20):
    """Garantiza la exclusión mutua usando DynamoDB antes de procesar el lote."""
    current_time = int(time.time())
    expires_at = current_time + ttl_seconds
    try:
        dynamodb_client.put_item(
            TableName=LOCK_TABLE,
            Item={
                'LockID': {'S': lock_id},
                'Status': {'S': 'LOCKED'},
                'ExpiresAt': {'N': str(expires_at)}
            },
            ConditionExpression='attribute_not_exists(LockID) OR ExpiresAt < :now',
            ExpressionAttributeValues={':now': {'N': str(current_time)}}
        )
        print(f"🔒 [Lock] Candado adquirido con éxito para la tarea: {lock_id}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print(f"⚠️ [Lock] La ejecución {lock_id} ya está bloqueada por otra instancia.")
            return False
        raise e

def release_lock(dynamodb_client, lock_id):
    """Libera el candado al terminar."""
    try:
        dynamodb_client.delete_item(TableName=LOCK_TABLE, Key={'LockID': {'S': lock_id}})
        print(f"🔓 [Lock] Candado liberado para la tarea: {lock_id}")
    except Exception as e:
        print(f"❌ Error al liberar candado {lock_id}: {str(e)}")

# =========================================================
# FLUJO DE DATOS Y FILTRADO (S3 INTAKE)
# =========================================================
def s3_telemetry_streamer(s3_client, bucket, key, simulation_mode=False):
    if simulation_mode:
        print("🛠️  [Simulación] Fabricando flujo de datos local en memoria...")
        s3_data = (
            "timestamp,vehicle_id,engine_rpm,coolant_temp_c,fault_code\n"
            f"{datetime.now()},VIN-999111,2500,95,P0300\n"
            f"{datetime.now()},VIN-222333,1800,88,NONE\n"
            f"{datetime.now()},VIN-444555,3100,102,P0171\n"
        )
    else:
        # Consume directo el S3 de LocalStack
        try:
            response = s3_client.get_object(Bucket=bucket, Key=key)
            s3_data = response["Body"].read().decode("utf-8")
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                print(f"⚠️ [S3] No se encontró el archivo '{key}'. Creando lote inicial de 1000 filas...")
                headers = "timestamp,vehicle_id,engine_rpm,coolant_temp_c,fault_code\n"
                bulk_data = headers
                for i in range(1, 1001):
                    code = "P0300" if i % 50 == 0 else "P0171" if i % 75 == 0 else "NONE"
                    bulk_data += f"{datetime.now()},VIN-{100000 + i},2100,90,{code}\n"
                s3_client.put_object(Bucket=bucket, Key=key, Body=bulk_data.encode("utf-8"))
                s3_data = bulk_data
            else:
                raise e
    
    LOCAL_INPUT_ARCHIVE.mkdir(parents=True, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    local_raw_file = LOCAL_INPUT_ARCHIVE / f"raw_s3_mirror_{timestamp_str}.csv"
    local_raw_file.write_text(s3_data, encoding="utf-8")
    print(f"💾 [Auditoría Local] Réplica cruda de entrada guardada en: {local_raw_file.relative_to(BASE_DIR)}")

    stream_buffer = io.StringIO(s3_data)
    stream_buffer.readline()
    
    for line in stream_buffer:
        if line.strip():
            row = line.strip().split(",")
            yield {
                "timestamp": row[0],
                "vehicle_id": row[1],
                "engine_rpm": int(row[2]),
                "coolant_temp_c": int(row[3]),
                "fault_code": row[4]
            }

def telemetry_processor(data_entry):
    if data_entry["fault_code"] == "NONE":
        return None
    processed_entry = data_entry.copy()
    processed_entry["alert_status"] = "⚠️ CRITICAL DEVIATION DETECTED"
    processed_entry["processed_at"] = str(datetime.now())
    return processed_entry

def local_bulk_writer(s3_client, bucket, blob_name, processed_records, simulation_mode=False):
    if not processed_records:
        print("📥 No se encontraron alertas críticas en este lote.")
        return
    
    headers = "timestamp,vehicle_id,engine_rpm,coolant_temp_c,fault_code,alert_status,processed_at\n"
    csv_buffer = headers
    for record in processed_records:
        csv_buffer += (
            f"{record['timestamp']},{record['vehicle_id']},{record['engine_rpm']},"
            f"{record['coolant_temp_c']},{record['fault_code']},{record['alert_status']},"
            f"{record['processed_at']}\n"
        )
    
    if simulation_mode:
        print("☁️  [Simulación] Modo local activo. Se saltó la carga real de salida.")
    else:
        output_key = f"processed_outputs/{blob_name}"
        s3_client.put_object(Bucket=bucket, Key=output_key, Body=csv_buffer.encode("utf-8"))
        print(f"☁️  [LocalStack] Transmisión exitosa a S3 de salida: {output_key}")
    
    LOCAL_OUTPUT_ARCHIVE.mkdir(parents=True, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    local_clean_file = LOCAL_OUTPUT_ARCHIVE / f"clean_alerts_{timestamp_str}.csv"
    local_clean_file.write_text(csv_buffer, encoding="utf-8")
    print(f"💾 [Auditoría Local] Reporte filtrado guardado en: {local_clean_file.relative_to(BASE_DIR)}")

# =========================================================
# BUCLE DE ORQUESTACIÓN PRINCIPAL (CON RESOLUCIÓN DNS)
# =========================================================
if __name__ == '__main__':
    # Sanitización radical de cadenas
    CLEAN_ENDPOINT = AWS_ENDPOINT.replace('"', '').replace("'", "").strip()
    CLEAN_ENDPOINT = "".join(CLEAN_ENDPOINT.split())
    
    # RESOLUCIÓN DE HOST: Forzamos la IP interna si el contenedor está presente
    if "localstack_simulador" in CLEAN_ENDPOINT:
        try:
            host = "localstack_simulador"
            ip_resolvida = socket.gethostbyname(host)
            CLEAN_ENDPOINT = CLEAN_ENDPOINT.replace(host, ip_resolvida)
            print(f"🌐 [DNS Docker] Nombre '{host}' traducido exitosamente a la IP: {ip_resolvida}")
        except Exception as dns_err:
            print(f"⚠️ Esperando inicialización de red de Docker para resolver DNS: {str(dns_err)}")

    print(f"📡 Verificando conexión con LocalStack en: '{CLEAN_ENDPOINT}' ...")
    
    s3 = None
    dynamodb_client = None
    
    for intento in range(1, 11):
        try:
            # Re-intentamos resolver por DNS en cada vuelta por si LocalStack tardó en levantar
            if "localstack_simulador" in CLEAN_ENDPOINT:
                try:
                    ip_resolvida = socket.gethostbyname("localstack_simulador")
                    CLEAN_ENDPOINT = CLEAN_ENDPOINT.replace("localstack_simulador", ip_resolvida)
                except Exception:
                    pass

            s3 = boto3.client(
                "s3", 
                endpoint_url=CLEAN_ENDPOINT, 
                region_name="us-east-1",
                aws_access_key_id="mock_key",
                aws_secret_access_key="mock_secret"
            )
            dynamodb_client = boto3.client(
                "dynamodb", 
                endpoint_url=CLEAN_ENDPOINT, 
                region_name="us-east-1",
                aws_access_key_id="mock_key",
                aws_secret_access_key="mock_secret"
            )
            
            # Intento de comunicación real para validar el endpoint
            s3.list_buckets()
            print("✅ Conexión exitosa con LocalStack. Clientes inicializados.")
            break
        except Exception as e:
            print(f"⏳ [Intento {intento}/10] LocalStack no responde. Detalle: {str(e)}")
            print("Esperando 5 segundos...")
            time.sleep(5)
    else:
        print("❌ No se pudo establecer conexión con LocalStack después de 50 segundos. Abortando.")
        exit(1)

    # Asegurar que la infraestructura exista en LocalStack si no estamos en simulación
    if not SIMULATION_MODE:
        # 1. Validación del Bucket S3
        try:
            s3.create_bucket(Bucket=AWS_BUCKET)
            print(f"📦 [LocalStack] Bucket de S3 verificado/creado: {AWS_BUCKET}")
        except Exception:
            pass 

        # 2. Validación y creación de la Tabla DynamoDB para Bloqueos
        try:
            print(f"🗄️  [LocalStack] Verificando existencia de tabla DynamoDB: {LOCK_TABLE} ...")
            dynamodb_client.create_table(
                TableName=LOCK_TABLE,
                AttributeDefinitions=[
                    {'AttributeName': 'LockID', 'AttributeType': 'S'}
                ],
                KeySchema=[
                    {'AttributeName': 'LockID', 'KeyType': 'HASH'}
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            print(f"✅ [LocalStack] Tabla '{LOCK_TABLE}' creada exitosamente.")
            
            # Esperar hasta que LocalStack confirme la disponibilidad de la tabla
            waiter = dynamodb_client.get_waiter('table_exists')
            waiter.wait(TableName=LOCK_TABLE)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"ℹ️  [LocalStack] La tabla '{LOCK_TABLE}' ya existe. Continuando...")
            else:
                print(f"❌ Error inesperado creando la tabla DynamoDB: {str(e)}")
                raise e

    while True:
        execution_id = f"cron_batch_{datetime.now().strftime('%Y%m%d_%H%M')}"
        
        if acquire_lock(dynamodb_client, execution_id):
            try:
                print("📥 Connecting to S3 Intake Stream...")
                data_stream = s3_telemetry_streamer(s3, AWS_BUCKET, AWS_KEY, simulation_mode=SIMULATION_MODE)
                
                incidents = []
                for raw_row in data_stream:
                    clean_row = telemetry_processor(raw_row)
                    if clean_row:
                        incidents.append(clean_row)
                        
                print(f"📤 Preparing handoff for {len(incidents)} processed records...")
                local_bulk_writer(s3, AWS_BUCKET, f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", incidents, simulation_mode=SIMULATION_MODE)
                
                print("🏁 Batch complete! Multi-cloud architectural loop completed successfully.")
            finally:
                release_lock(dynamodb_client, execution_id)
        
        print("⏰ Esperando 15 segundos para la siguiente iteración del planificador...")
        time.sleep(15)