# Pruebas unitarias para la lógica de procesamiento de telemetría de vehículos

def telemetry_processor(data_entry):
    if data_entry.get("fault_code") == "NONE":
        return None
    processed_entry = data_entry.copy()
    processed_entry["alert_status"] = "⚠️ CRITICAL DEVIATION DETECTED"
    return processed_entry

def test_telemetry_processor_critical():
    raw_data = {
        "vehicle_id": "VIN-100200",
        "engine_rpm": 3200,
        "coolant_temp_c": 105,
        "fault_code": "P0300"
    }
    result = telemetry_processor(raw_data)
    assert result is not None
    assert result["alert_status"] == "⚠️ CRITICAL DEVIATION DETECTED"

def test_telemetry_processor_normal():
    raw_data = {
        "vehicle_id": "VIN-100201",
        "engine_rpm": 2100,
        "coolant_temp_c": 90,
        "fault_code": "NONE"
    }
    result = telemetry_processor(raw_data)
    assert result is None
