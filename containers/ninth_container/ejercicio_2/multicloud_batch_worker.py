import io
import os
from pathlib import Path
from datetime import datetime
import boto3
from botocore.config import Config
from azure.storage.blob import BlobServiceClient

import os
from pathlib import Path

# =========================================================
# CAPTURA DE VARIABLES DE ENTORNO (EL PUENTE CON DOCKER)
# =========================================================

# os.environ.get busca la variable en Docker. Si no la encuentra, usa el valor por defecto.
# IMPORTANTE: Docker todo lo manda como texto ("True" o "False").
# Por eso lo comparamos con el texto "True" para convertirlo en un Booleano real de Python.
SIMULATION_ENV = os.environ.get("SIMULACION", "True")
SIMULATION_MODE = SIMULATION_ENV.upper() == "TRUE"

# Capturamos el resto de las variables que configuraste en el YAML
AWS_BUCKET = os.environ.get("AWS_INPUT_BUCKET", "fleet-raw-data")
AWS_KEY = os.environ.get("AWS_INPUT_KEY", "raw_telemetry.csv")
AZURE_CONTAINER = os.environ.get("AZURE_OUTPUT_CONTAINER", "fleet-clean-alerts")

print(f"🚀 Live Enterprise Multi-Cloud Pipeline Booting Up...")
print(f"🎛️  Modo de Simulación: {'ACTIVADO (3 filas)' if SIMULATION_MODE else 'DESACTIVADO (1,000 filas con AWS S3)'}")
####################
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
    else:
        container_client.upload_blob(name=blob_name, data=csv_buffer, overwrite=True)
        print("☁️  [Cloud] Transmisión exitosa a Azure Blob Storage.")
    
    LOCAL_OUTPUT_ARCHIVE.mkdir(parents=True, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    local_clean_file = LOCAL_OUTPUT_ARCHIVE / f"clean_alerts_{timestamp_str}.csv"
    local_clean_file.write_text(csv_buffer, encoding="utf-8")
    print(f"💾 [Auditoría Local] Reporte filtrado guardado en: {local_clean_file.relative_to(BASE_DIR)}")

if __name__ == '__main__':
    print("🚀 Live Enterprise Multi-Cloud Pipeline Booting Up...")
    
    AWS_BUCKET = os.getenv("AWS_INPUT_BUCKET", "dev-fleet-raw-data")
    AWS_KEY = os.getenv("AWS_INPUT_KEY", "daily_telemetry.csv")
    AZURE_CONTAINER = os.getenv("AZURE_OUTPUT_CONTAINER", "dev-fleet-alerts")
    
    SIMULACION = os.getenv("SIMULACION", "True").upper() == "TRUE"
    
    s3, azure_container_client = None, None
    
    if not SIMULACION:
        print("⚡ [Modo Enterprise Local] Inicializando entorno simulado de AWS S3 con Moto...")
        
        # 1. ACTIVAR EL MOCK DE MOTO PARA INTERCEPTAR AWS
        from moto import mock_aws
        
        # Iniciamos el contexto simulado de AWS
        mock_context = mock_aws()
        mock_context.start()
        
        # Creamos el cliente S3 virtual apuntando al entorno local en memoria
        s3 = boto3.client("s3", region_name="us-east-1")
        
        # Creamos el bucket virtual y le inyectamos los 1,000 registros ficticios de telemetría
        s3.create_bucket(Bucket=AWS_BUCKET)
        
        # Fabricamos un lote masivo de telemetría simulada (1,000 líneas) para la prueba
        headers = "timestamp,vehicle_id,engine_rpm,coolant_temp_c,fault_code\n"
        bulk_data = headers
        for i in range(1, 1001):
            code = "P0300" if i % 50 == 0 else "P0171" if i % 75 == 0 else "NONE"
            bulk_data += f"{datetime.now()},VIN-{100000 + i},2100,90,{code}\n"
            
        # Subimos el lote masivo al AWS S3 simulado en memoria
        s3.put_object(Bucket=AWS_BUCKET, Key=AWS_KEY, Body=bulk_data.encode("utf-8"))
        print(f"📦 [S3 Mock] Archivo '{AWS_KEY}' con 1,000 registros cargado con éxito en el Bucket virtual.")
        
        # Simulador local para Azure (Mock)
        class LocalMockAzureContainer:
            def upload_blob(self, name, data, overwrite=True):
                print(f"☁️  [Local Container] Reporte '{name}' interceptado exitosamente en simulación local.")
        
        azure_container_client = LocalMockAzureContainer()
        
    else:
        print("⚠️  Advertencia: Modo de Simulación de 3 filas en memoria Activo.")
    
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