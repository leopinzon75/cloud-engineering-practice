import pytest
import boto3
from moto import mock_aws
from pathlib import Path
from app import app, BUCKET_NAME

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@mock_aws
def test_home_page(client):
    """Verifica que el portal principal cargue correctamente."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Diagnostic Web Portal Active" in response.get_data(as_text=True)

@mock_aws
def test_diagnostics_auto_seed(client):
    """Prueba que el escáner cree la nube simulada e inyecte el reporte inicial."""
    # 1. Crear el bucket en la nube simulada
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=BUCKET_NAME)

    # 2. Consultar la ruta de diagnóstico
    response = client.get("/diagnostics")
    assert response.status_code == 200
    assert "P0300" in response.get_data(as_text=True)

@mock_aws
def test_submit_new_report_dual_write(client):
    """Prueba la escritura dual: guarda en la nube simulada y en el disco local."""
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=BUCKET_NAME)

    payload = {
        "code": "P0171 - System Too Lean",
        "vehicle": "VIN-TEST-1234"
    }

    # Enviamos el formulario vía POST
    response = client.post("/report", data=payload)
    assert response.status_code == 200
    assert "Report Saved Successfully" in response.get_data(as_text=True)

    # Verificación 1: Confirmar escritura en la Nube Simulada (S3)
    s3_object = s3.get_object(Bucket=BUCKET_NAME, Key="fault_VIN-TEST-1234.txt")
    s3_content = s3_object["Body"].read().decode("utf-8")
    assert "P0171" in s3_content

    # Verificación 2: Confirmar escritura en el Disco Local
    local_file = Path.cwd() / "output" / "fault_VIN-TEST-1234.txt"
    assert local_file.exists()
    assert "P0171" in local_file.read_text(encoding="utf-8")
