from pathlib import Path
import pytest
from app import telemetry_processor, telemetry_streamer

def test_telemetry_processor_ignores_none():
    sample_entry = {
        "timestamp": "2026-08-03 12:00:00",
        "vehicle_id": "VIN-123456",
        "engine_rpm": 2500,
        "coolant_temp_c": 90,
        "fault_code": "NONE"
    }
    result = telemetry_processor(sample_entry)
    assert result is None

def test_telemetry_processor_flags_critical_code():
    sample_entry = {
        "timestamp": "2026-08-03 12:00:00",
        "vehicle_id": "VIN-123456",
        "engine_rpm": 2500,
        "coolant_temp_c": 90,
        "fault_code": "P0171"
    }
    result = telemetry_processor(sample_entry)
    assert result is not None
    assert result["fault_code"] == "P0171"
    assert "CRITICAL DEVIATION DETECTED" in result["alert_status"]
