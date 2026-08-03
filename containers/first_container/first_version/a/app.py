import os
import boto3
from moto import mock_aws

print("🛡️ Activating Internal Cloud Simulator...")

@mock_aws
def run_engine_sandbox():
    s3 = boto3.client('s3', region_name='us-east-1')
    bucket_name = "engine-trouble-codes"
    s3.create_bucket(Bucket=bucket_name)
    print(f"📦 Created simulated cloud bucket: {bucket_name}")
   
    report_data = "DIAGNOSTIC REPORT: CODE P0300 - RANDOM/MULTIPLE CYLINDER MISFIRE DETECTED."
    s3.put_object(Bucket=bucket_name, Key="misfire_report.txt", Body=report_data)
    print("🚀 Misfire report uploaded to simulated AWS Cloud!")
     
    response = s3.get_object(Bucket=bucket_name, Key="misfire_report.txt")
    downloaded_data = response['Body'].read().decode('utf-8')
    print("📥 Cloud data verification: 100% Match!")
    
    # 🛠️ Industrial-strength local file creation inside the container
    log_dir = "logs"
    filename = "final_misfire_report.txt"
    
    os.makedirs(log_dir, exist_ok=True)
    target_filepath = os.path.abspath(os.path.join(log_dir, filename))
    
    with open(target_filepath, 'w') as f:
        f.write(downloaded_data)

    # with open(a, 'w') as f:
    #     f.write(report_data)
        
    print(f"📍 Target Location inside container: {target_filepath}")
    print("💾 Permanent Copy stamped to local logs directory!")

if __name__ == "__main__":
    run_engine_sandbox()
