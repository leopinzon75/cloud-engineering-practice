import os
import pytest
import boto3
from moto import mock_aws
from app import MockBlobServiceClient

def test_local_data_file_creation():
    assert os.path.exists(os.path.join("fleet_data", "raw_fleet_telemetry.csv"))

@mock_aws
def test_s3_simulation():
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="test-bucket")
    s3.put_object(Bucket="test-bucket", Key="test.txt", Body=b"hello multi-cloud")
    
    response = s3.get_object(Bucket="test-bucket", Key="test.txt")
    content = response["Body"].read().decode("utf-8")
    assert content == "hello multi-cloud"

def test_azure_mock_client():
    azure_client = MockBlobServiceClient()
    container = azure_client.get_container_client("fleet-clean-alerts")
    container.upload_blob("alert_01.csv", b"timestamp,vehicle_id,fault_code\n")
    assert "alert_01.csv" in container.stored_blobs
