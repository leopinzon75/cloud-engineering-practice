import pytest
from pathlib import Path
from app import telemetry_processor, telemetry_streamer

# 1. Test unitario del procesador de telemetría (Filtro NONE)
def test_telemetry_processor_descarta_none():
    data_ok = {
        "timestamp": "2026-08-03 10:00:00",
        "vehicle_id": "VIN-123456",
        "engine_rpm": 2000,
        "coolant_temp_c": 90,
        "fault_code": "NONE"
    }
    assert telemetry_processor(data_ok) is None

# 2. Test unitario del procesador de telemetría (Enriquecimiento de Falla)
def test_telemetry_processor_enriquece_falla():
    data_falla = {
        "timestamp": "2026-08-03 10:00:00",
        "vehicle_id": "VIN-654321",
        "engine_rpm": 3000,
        "coolant_temp_c": 100,
        "fault_code": "P0171"
    }
    resultado = telemetry_processor(data_falla)
    assert resultado is not None
    assert resultado["alert_status"] == "⚠️ CRITICAL DEVIATION DETECTED"
    assert "processed_at" in resultado

# 3. Test de integración del streamer con un archivo temporal (tmp_path)
def test_telemetry_streamer(tmp_path):
    test_csv = tmp_path / "test_input.csv"
    test_csv.write_text(
        "timestamp,vehicle_id,engine_rpm,coolant_temp_c,fault_code\n"
        "2026-08-03 10:00:00,VIN-000001,2200,92,P0300\n",
        encoding="utf-8"
    )
    
    gen = telemetry_streamer(test_csv)
    item = next(gen)
    
    assert item["vehicle_id"] == "VIN-000001"
    assert item["engine_rpm"] == 2200
    assert item["fault_code"] == "P0300"
