import pytest
import boto3
from moto import mock_aws
import os

# Configurar credenciales ficticias antes de importar app
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["BUCKET_NAME"] = "vehicle-diagnostic-vault"

from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@mock_aws
def test_seed_endpoint(client):
    """Prueba la siembra del código de falla en S3 usando un mock."""
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="vehicle-diagnostic-vault")

    response = client.get("/seed")
    assert response.status_code == 200
    assert b"Seeded fault code P0171" in response.data

@mock_aws
def test_diagnostics_endpoint(client):
    """Prueba la lectura del código de falla desde S3 usando un mock."""
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="vehicle-diagnostic-vault")
    s3.put_object(
        Bucket="vehicle-diagnostic-vault",
        Key="live_fault_code.txt",
        Body="P0171 - System Too Lean (Bank 1)"
    )

    response = client.get("/diagnostics")
    assert response.status_code == 200
    assert b"P0171" in response.data
