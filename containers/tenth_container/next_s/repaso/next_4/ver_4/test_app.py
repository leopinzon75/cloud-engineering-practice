import os
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_status(client):
    """Verifica que el endpoint principal responda 200 OK"""
    response = client.get('/')
    assert response.status_code == 200

def test_environment_variables():
    """Verifica la lectura de configuraciones"""
    # Prueba de lectura de entorno
    assert os.getenv('FLASK_APP', 'app.py') == 'app.py'
