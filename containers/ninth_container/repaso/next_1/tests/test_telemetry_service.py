import sys
import os
import pytest

# Agregar el directorio actual al path para encontrar app.py
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from app import analyze_vehicle_telemetry

def test_telemetry_normal_operation():
    payload = {
        "vehicle_id": "VIN-101",
        "engine_rpm": 2200,
        "coolant_temp_c": 90,
        "fault_code": "NONE"
    }
    response = analyze_vehicle_telemetry(payload)
    assert response["status"] == "NORMAL"
    assert response["vehicle_id"] == "VIN-101"

def test_telemetry_overheating_critical():
    payload = {
        "vehicle_id": "VIN-102",
        "engine_rpm": 2500,
        "coolant_temp_c": 110, # Sobrecalentamiento
        "fault_code": "NONE"
    }
    response = analyze_vehicle_telemetry(payload)
    assert response["status"] == "CRITICAL"

def test_telemetry_fault_code_critical():
    payload = {
        "vehicle_id": "VIN-103",
        "engine_rpm": 1800,
        "coolant_temp_c": 88,
        "fault_code": "P0300" # Falla de encendido
    }
    response = analyze_vehicle_telemetry(payload)
    assert response["status"] == "CRITICAL"

def test_telemetry_invalid_input():
    with pytest.raises(ValueError):
        analyze_vehicle_telemetry("formato_invalido_no_dict")
