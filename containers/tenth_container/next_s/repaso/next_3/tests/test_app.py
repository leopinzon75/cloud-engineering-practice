import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    """Verifica que la ruta principal responda correctamente"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Cloud-Connected Diagnostic Portal Active" in response.data
