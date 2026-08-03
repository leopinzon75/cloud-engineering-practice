import random
from datetime import datetime, timedelta
from pathlib import Path
import sys

# ==========================================
# 1. DEFINICIÓN DE ENTORNOS CON PATHLIB
# ==========================================
BASE_DIR = Path.cwd()
INPUT_DIR = BASE_DIR / "data" / "input"
OUTPUT_DIR = BASE_DIR / "data" / "output"

# Garantizar de manera defensiva que existan las carpetas
try:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Entorno listo en el directorio de trabajo: {BASE_DIR}")
except Exception as e:
    print(f"❌ Error al inicializar el entorno de carpetas: {e}")
    sys.exit(1)

# Definir las rutas exactas de los archivos usando objetos Path
input_file_path = INPUT_DIR / "raw_fleet_telemetry.csv"
output_file_path = OUTPUT_DIR / "clean_critical_incidents.csv"

# ==========================================
# 2. GENERADOR DE DATOS (Tus 10,000 filas)
# ==========================================
start_time = datetime.now()
fault_codes = ["P0171", "P0300", "P0420", "NONE", "NONE", "NONE", "NONE"]

print("⚡ Manufacturing 10,000 data rows into input directory...")

with open(input_file_path, "w", encoding="utf-8") as f:
    f.write("timestamp,vehicle_id,engine_rpm,coolant_temp_c,fault_code
")
    
    for i in range(10000):
        timestamp = start_time + timedelta(seconds=i)
        v_id = f"VIN-{random.randint(000000, 999999)}"
        rpm = random.randint(1500, 3500) if random.random() > 0.05 else 0  
        temp = random.randint(85, 105)
        code = random.choice(fault_codes)
        
        f.write(f"{timestamp},{v_id},{rpm},{temp},{code}
")

print(f"📝 Step 1 Complete: Created '{input_file_path.name}' with 10,000 rows!")

# ==========================================
# 3. PIPELINE DE PROCESAMIENTO (Batch Worker Moderno)
# ==========================================
def telemetry_streamer(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        header = f.readline()  # Omitir encabezado
        for line in f:
            if not line.strip():
                continue
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

def telemetry_writer(output_path: Path, processed_entry):
    with open(output_path, "a", encoding="utf-8") as f:
        line = (
            f"{processed_entry['timestamp']},"
            f"{processed_entry['vehicle_id']},"
            f"{processed_entry['engine_rpm']},"
            f"{processed_entry['coolant_temp_c']},"
            f"{processed_entry['fault_code']},"
            f"{processed_entry['alert_status']},"
            f"{processed_entry['processed_at']}
"
        )
        f.write(line)

# ==========================================
# 4. EJECUCIÓN DEL PROCESO
# ==========================================
if input_file_path.exists():
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write("timestamp,vehicle_id,engine_rpm,coolant_temp_c,fault_code,alert_status,processed_at
")
        
    print("
🚀 Cloud Batch Engine running with Pathlib (Processing 10k rows)...")
    
    stream = telemetry_streamer(input_file_path)
    count = 0
    
    for raw in stream:
        enriched = telemetry_processor(raw)
        if enriched:
            telemetry_writer(output_file_path, enriched)
            count += 1
            
    print(f"🏁 Batch complete! Wrote {count} critical diagnostic incidents to {output_file_path.relative_to(BASE_DIR)}")
else:
    print(f"❌ Error: El archivo generado no se encuentra en {input_file_path}")