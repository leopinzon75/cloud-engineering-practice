import pytest
from unittest.mock import patch, MagicMock
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    """Prueba que la ruta principal responda correctamente."""
    response = client.get('/')
    assert response.status_code == 200
    assert "Cloud-Connected Diagnostic Portal Active" in response.get_data(as_text=True)

@patch('app.s3')
def test_seed_data_success(mock_s3, client):
    """Prueba que el endpoint /seed envíe datos a S3."""
    mock_s3.head_bucket.return_value = {}
    mock_s3.put_object.return_value = {}

    response = client.get('/seed')
    assert response.status_code == 200
    assert "Seeded fault code P0171 into MinIO S3!" in response.get_data(as_text=True)
    mock_s3.put_object.assert_called_once()

@patch('app.s3')
def test_diagnostics_success(mock_s3, client):
    """Prueba la lectura correcta de datos desde el bucket S3."""
    mock_s3.head_bucket.return_value = {}
    
    # Usar .encode('utf-8') para convertir texto con emojis a bytes sin SyntaxError
    mock_body = MagicMock()
    mock_body.read.return_value = "🚨 CLOUD DATA: P0171 - System Too Lean (Bank 1)".encode('utf-8')
    mock_s3.get_object.return_value = {"Body": mock_body}

    response = client.get('/diagnostics')
    assert response.status_code == 200
    assert "P0171 - System Too Lean" in response.get_data(as_text=True)
