import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# 1. Prueba de la ruta raíz (/)
def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Cloud-Connected Diagnostic Portal Active" in response.data

# 2. Prueba de la ruta /seed simulando put_object con Mock
@patch('app.s3')
def test_seed_data(mock_s3, client):
    mock_s3.head_bucket.return_value = {}
    mock_s3.put_object.return_value = {}
    
    response = client.get('/seed')
    assert response.status_code == 200
    assert b"Seeded fault code P0171 into MinIO S3!" in response.data
    mock_s3.put_object.assert_called_once()

# 3. Prueba de la ruta /diagnostics exitosa
@patch('app.s3')
def test_diagnostics_success(mock_s3, client):
    mock_s3.head_bucket.return_value = {}
    
    # Simular lectura del Stream de Boto3 Body
    mock_body = MagicMock()
    mock_body.read.return_value = "🚨 CLOUD DATA: P0171 - System Too Lean (Bank 1)".encode('utf-8')
    mock_s3.get_object.return_value = {"Body": mock_body}

    response = client.get('/diagnostics')
    assert response.status_code == 200
    assert b"P0171" in response.data

# 4. Prueba del endpoint /health (Salud del servicio)
@patch('app.s3')
def test_health_check(mock_s3, client):
    mock_s3.list_buckets.return_value = {"Buckets": []}
    
    response = client.get('/health')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "healthy"
    assert json_data["s3_connection"] == "ok"
