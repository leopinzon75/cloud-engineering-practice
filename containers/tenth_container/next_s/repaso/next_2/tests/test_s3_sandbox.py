import sys
import os
import pytest
import boto3
from moto import mock_aws

# Corregir la ruta para importar app.py desde el directorio superior
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from app import run_engine_sandbox, BUCKET_NAME

@mock_aws
def test_run_engine_sandbox_flow():
    """
    Prueba el flujo completo de S3 usando un mock en memoria (moto).
    """
    # 1. Crear cliente S3 simulado
    s3_mock = boto3.client('s3', region_name='us-east-1')
    
    # 2. Ejecutar la función principal pasando el mock
    content = run_engine_sandbox(custom_s3_client=s3_mock)
    
    # 3. Asserts / Verificaciones
    assert "P0300" in content
    
    # Verificar que el objeto existe en S3
    response = s3_mock.get_object(Bucket=BUCKET_NAME, Key="misfire_report.txt")
    retrieved_text = response['Body'].read().decode('utf-8')
    assert "RANDOM/MULTIPLE CYLINDER MISFIRE DETECTED" in retrieved_text
    
    # Verificar que el log local fue escrito correctamente
    assert os.path.exists("logs/final_misfire_report.txt")
