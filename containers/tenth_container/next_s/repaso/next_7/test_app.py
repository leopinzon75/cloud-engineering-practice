import pytest
from app import telemetry_processor

def test_telemetry_processor_ignores_none():
    sample_none = {
        "timestamp": "2026-07-30 12:00:00",
        "vehicle_id": "VIN-123456",
        "engine_rpm": 2200,
        "coolant_temp_c": 90,
        "fault_code": "NONE"
    }
    assert telemetry_processor(sample_none) is None

def test_telemetry_processor_detects_fault():
    sample_fault = {
        "timestamp": "2026-07-30 12:00:00",
        "vehicle_id": "VIN-654321",
        "engine_rpm": 2800,
        "coolant_temp_c": 98,
        "fault_code": "P0300"
    }
    result = telemetry_processor(sample_fault)
    assert result is not None
    assert result["fault_code"] == "P0300"
    assert "alert_status" in result
