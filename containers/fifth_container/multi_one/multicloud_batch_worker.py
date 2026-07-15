import io
import os
from pathlib import Path
from datetime import datetime
import boto3
from botocore.config import Config
from azure.storage.blob import BlobServiceClient

BASE_DIR = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
LOCAL_INPUT_ARCHIVE = BASE_DIR / "data" / "archive" / "input"
LOCAL_OUTPUT_ARCHIVE = BASE_DIR / "data" / "archive" / "output"

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
        response = s3_client.get_object(Bucket=bucket, Key=key)
        s3_data = response["Body"].read().decode("utf-8")
    
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

def azure_bulk_writer(container_client, blob_name, processed_records, simulation_mode=False):
    if not processed_records:
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
        print("☁️  [Simulación] Modo local activo. Se saltó la carga real a Azure.")
    # 1. Si se envia directo a la nube de Azure
    else:
        container_client.upload_blob(name=blob_name, data=csv_buffer, overwrite=True)
        print("☁️  [Cloud] Transmisión exitosa a Azure Blob Storage.")

    
# 2. --- Modernización Dual: Guardar réplica local del reporte procesado ---
    LOCAL_OUTPUT_ARCHIVE.mkdir(parents=True, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    local_clean_file = LOCAL_OUTPUT_ARCHIVE / f"clean_alerts_{timestamp_str}.csv"
    local_clean_file.write_text(csv_buffer, encoding="utf-8")
    print(f"💾 [Auditoría Local] Reporte filtrado guardado en: {local_clean_file.relative_to(BASE_DIR)}")

if __name__ == '__main__':
    print("🚀 Live Enterprise Multi-Cloud Pipeline Booting Up...")
    
    # Configuración de variables de entorno de producción
    AWS_BUCKET = os.getenv("AWS_INPUT_BUCKET", "prod-fleet-raw-data")
    AWS_KEY = os.getenv("AWS_INPUT_KEY", "daily_telemetry.csv")
    AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_CONTAINER = os.getenv("AZURE_OUTPUT_CONTAINER", "prod-fleet-alerts")
    
    # Modo de simulación local si faltan credenciales en desarrollo
    SIMULACION = False
    if not AZURE_CONNECTION_STRING:
        print("⚠️  Advertencia: Variables de entorno Cloud no detectadas.")
        print("🔄  Activando Modo de Simulación de Infraestructura Local...")
        SIMULACION = True
        
    s3, azure_container_client = None, None
    if not SIMULACION:
        aws_enterprise_config = Config(
            connect_timeout=5,
            read_timeout=10,
            retries={'max_attempts': 3, 'mode': 'standard'}
        )
        # Inicialización de clientes Cloud de nivel Enterprise
        s3 = boto3.client("s3", config=aws_enterprise_config)
        azure_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        azure_container_client = azure_service_client.get_container_client(AZURE_CONTAINER)
    
    print("📥 Connecting to S3 Intake Stream...")
    data_stream = s3_telemetry_streamer(s3, AWS_BUCKET, AWS_KEY, simulation_mode=SIMULACION)
    
    incidents = []
    for raw_row in data_stream:
        clean_row = telemetry_processor(raw_row)
        if clean_row:
            incidents.append(clean_row)
            
    print(f"📤 Preparing handoff for {len(incidents)} processed records...")
    azure_bulk_writer(azure_container_client, "critical_incidents_report.csv", incidents, simulation_mode=SIMULACION)
    
    print("🏁 Batch complete! Multi-cloud architectural loop completed successfully.")
