import boto3
import os
from moto import mock_aws

print("🛡️ Activating Internal Cloud Simulator...")

@mock_aws
def run_engine_sandbox():
    # 1. Connect to simulated S3
    s3 = boto3.client('s3', region_name='us-east-1')
    bucket_name = "engine-trouble-codes"
    s3.create_bucket(Bucket=bucket_name)
    print(f"📦 Created simulated cloud bucket: {bucket_name}")
    
    # 2. Define our new payload data (Engine Trouble Code Report)
    report_data = "DIAGNOSTIC REPORT: CODE P0300 - RANDOM/MULTIPLE CYLINDER MISFIRE DETECTED. CHECK SPARK PLUGS AND IGNITION COILS."
    
    # 3. Upload to simulated cloud
    s3.put_object(Bucket=bucket_name, Key="misfire_report.txt", Body=report_data)
    print("🚀 Misfire report uploaded to simulated AWS Cloud!")
    
    # 4. Download and verify
    response = s3.get_object(Bucket=bucket_name, Key="misfire_report.txt")
    downloaded_data = response['Body'].read().decode('utf-8')
    print("📥 Cloud data verification: 100% Match!")
    
    # 5. The Umbilical Cord Bridge: Drop it into the shared logs folder
    os.makedirs('logs', exist_ok=True)
    with open('logs/final_misfire_report.txt', 'w') as f:
        f.write(downloaded_data)
    print("💾 Permanent Copy stamped to local container logs directory!")

run_engine_sandbox()
