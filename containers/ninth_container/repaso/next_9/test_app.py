import pytest
from app import telemetry_processor, s3_telemetry_streamer

def test_telemetry_processor_filtering():
    normal_entry = {
        "timestamp": "2026-07-31", "vehicle_id": "VIN-001",
        "engine_rpm": 2000, "coolant_temp_c": 90, "fault_code": "NONE"
    }
    fault_entry = {
        "timestamp": "2026-07-31", "vehicle_id": "VIN-002",
        "engine_rpm": 3000, "coolant_temp_c": 105, "fault_code": "P0300"
    }
    
    assert telemetry_processor(normal_entry) is None
    processed = telemetry_processor(fault_entry)
    assert processed is not None
    assert processed["fault_code"] == "P0300"
    assert "alert_status" in processed

def test_s3_telemetry_streamer_simulation():
    stream = s3_telemetry_streamer(None, "bucket", "key", simulation_mode=True)
    records = list(stream)
    assert len(records) == 3
    assert records[0]["vehicle_id"] == "VIN-999111"
