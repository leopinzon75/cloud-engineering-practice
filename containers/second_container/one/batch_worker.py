from pathlib import Path
from datetime import datetime
import sys

def telemetry_streamer(file_path: Path):
    # pathlib se integra directo con open()
    with open(file_path, "r") as f:
        header = f.readline()
        for line in f:
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

def telemetry_writer(output_file_path: Path, processed_entry):
    if processed_entry is not None:
        with open(output_file_path, "a") as f:
            line = f"{processed_entry['timestamp']},{processed_entry['vehicle_id']},{processed_entry['engine_rpm']},{processed_entry['coolant_temp_c']},{processed_entry['fault_code']},{processed_entry['alert_status']},{processed_entry['processed_at']}\n"
            f.write(line)

if __name__ == "__main__":
    # 1. Definición dinámica de Base Directory (Donde sea que corra el script)
    BASE_DIR = Path(__file__).resolve().parent
    
    # 2. Rutas dinámicas y robustas
    INPUT_DIR = BASE_DIR / "data" / "input"
    OUTPUT_DIR = BASE_DIR / "data" / "output"
    
    input_source = INPUT_DIR / "raw_fleet_telemetry.csv"
    output_destination = OUTPUT_DIR / "clean_critical_incidents.csv"
    
    # 3. Garantizar el entorno (Garantía de existencia)
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"❌ Error crítico al inicializar directorios: {e}")
        sys.exit(1)
        
    # 4. Verificación de existencia del archivo origen usando pathlib (.exists())
    if not input_source.exists():
        print(f"❌ Error: Archivo de entrada no encontrado en: {input_source}")
        sys.exit(1)
        
    # Inicializar archivo de salida con encabezados
    with open(output_destination, "w") as f:
        f.write("timestamp,vehicle_id,engine_rpm,coolant_temp_c,fault_code,alert_status,processed_at\n")
        
    print("🚀 Cloud Batch Engine running with Pathlib...")
    stream = telemetry_streamer(input_source)
    count = 0
    for raw in stream:
        enriched = telemetry_processor(raw)
        if enriched:
            telemetry_writer(output_destination, enriched)
            count += 1
            
    print(f"🏁 Batch complete! Wrote {count} incidents to {output_destination}")
