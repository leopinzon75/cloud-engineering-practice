import os
import random
from datetime import datetime, timedelta
from moto import mock_aws
import boto3

print("🔧 Step 1: Checking and preparing local workbench folders...")

# A. Create the fleet_data folder if it is missing
if not os.path.exists("fleet_data"):
    os.makedirs("fleet_data")
    print("📁 Created missing 'fleet_data' folder.")

local_raw_path = os.path.join("fleet_data", "raw_fleet_telemetry.csv")

# B. Manufacture a fresh 1,000-row telemetry dataset automatically
print("📝 Manufacturing fresh diagnostic data rows...")
with open(local_raw_path, "w") as f:
    f.write("timestamp,vehicle_id,engine_rpm,coolant_temp_c,fault_code")
    start_time = datetime.now()
    fault_codes = ["P0171", "P0300", "P0420", "NONE", "NONE", "NONE"]
    
    for i in range(1000):
        timestamp = start_time + timedelta(seconds=i)
        v_id = f"VIN-{random.randint(000, 1006)}"
        rpm = random.randint(1500, 3500)
        temp = random.randint(85, 105)
        code = random.choice(fault_codes)
        f.write(f"{timestamp},{v_id},{rpm},{temp},{code}")

print(f"✅ Telemetry data file successfully secured at: {local_raw_path}")


print("⚡ Step 2: Igniting the Multi-Cloud Local Simulator...")

# Stop any older stuck mock sessions if they are lingering
try:
    aws_mock.stop()
except:
    pass

# Start a fresh AWS Simulation
aws_mock = mock_aws()
aws_mock.start()

# Setup the Simulated AWS S3 Environment
s3_client = boto3.client("s3", region_name="us-east-1")
s3_bucket_name = "fleet-raw-data"
s3_client.create_bucket(Bucket=s3_bucket_name)

# Upload the file we just created into our virtual AWS cloud tank
s3_client.upload_file(local_raw_path, s3_bucket_name, "raw_telemetry.csv")
print("☁️ AWS S3 Simulation: Created bucket 'fleet-raw-data' and uploaded 'raw_telemetry.csv'")


# Setup our Simulated Azure Environment
class MockAzureContainerClient:
    def __init__(self):
        self.stored_blobs = {}
    def upload_blob(self, name, data, overwrite=True):
        self.stored_blobs[name] = data
        print(f"☁️ Microsoft Azure Simulation: Successfully intercepted and saved blob '{name}'!")

class MockBlobServiceClient:
    def get_container_client(self, container_name):
        print(f"☁️ Microsoft Azure Simulation: Connected to container '{container_name}'")
        return MockAzureContainerClient()

# Initialize our simulated Azure connection
azure_client = MockBlobServiceClient()
azure_container = azure_client.get_container_client("fleet-clean-alerts")

print("⚙️ Integration Complete: Multi-cloud local simulator is running flawlessly!")
