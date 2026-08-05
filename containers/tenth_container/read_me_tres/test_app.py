import boto3
from moto import mock_aws
from app import app, set_s3_client

@mock_aws
def test_seed_and_diagnostics():
    # 1. Crear el cliente mock de S3 e inyectarlo en la app
    mock_s3 = boto3.client("s3", region_name="us-east-1")
    set_s3_client(mock_s3)
    
    # 2. Usar el cliente de pruebas de Flask
    client = app.test_client()
    
    # 3. Guardar los datos (/seed)
    seed_res = client.get("/seed")
    assert seed_res.status_code == 200
    
    # 4. Leer los datos (/diagnostics) y verificar el código P0171
    diag_res = client.get("/diagnostics")
    assert diag_res.status_code == 200
    assert "P0171" in diag_res.get_data(as_text=True)
