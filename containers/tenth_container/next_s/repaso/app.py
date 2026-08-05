from datetime import datetime

def telemetry_processor(data_entry):
    if data_entry.get("fault_code") == "NONE":
        return None
    processed_entry = data_entry.copy()
    processed_entry["alert_status"] = "⚠️ CRITICAL DEVIATION DETECTED"
    processed_entry["processed_at"] = str(datetime.now())
    return processed_entry

if __name__ == "__main__":
    print("🚀 [GitHub Actions CD] Procesador de Telemetría iniciado correctamente.")
