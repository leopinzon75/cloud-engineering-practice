import pytest
import os
from pathlib import Path
from app import MockBlobServiceClient

def test_azure_simulation():
    azure_client = MockBlobServiceClient()
    container = azure_client.get_container_client("test-container")
    container.upload_blob("test.txt", "data")
    assert "test.txt" in container.stored_blobs

def test_fleet_data_creation():
    local_raw_path = Path("fleet_data") / "raw_fleet_telemetry.csv"
    assert local_raw_path.exists()
