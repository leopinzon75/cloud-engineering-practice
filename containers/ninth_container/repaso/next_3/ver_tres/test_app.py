import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_read_root_endpoint(client):
    """Prueba que el endpoint '/' devuelva HTTP status 200 y la estructura JSON correcta."""
    response = client.get('/')
    assert response.status_code == 200
    
    json_data = response.get_json()
    assert json_data is not None
    assert json_data['status'] == 'ok'
