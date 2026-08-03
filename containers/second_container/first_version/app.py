from flask import Flask
import boto3
from moto import mock_aws

app = Flask(__name__)

# Start the AWS simulation layer globally
mock = mock_aws()
mock.start()

# Connect to the mock S3 service and manufacture our bucket
s3 = boto3.client("s3", region_name="us-east-1")
BUCKET_NAME = "vehicle-diagnostic-vault"
s3.create_bucket(Bucket=BUCKET_NAME)

# Seed the cloud bucket with data: upload a trouble code file
s3.put_object(
    Bucket=BUCKET_NAME,
    Key="live_fault_code.txt",
    Body="🚨 CLOUD DATA: P0171 - System Too Lean (Bank 1)"
)

@app.route("/")
def home():
    return "<h1>🌐 Cloud-Connected Diagnostic Portal Active</h1>"

@app.route("/diagnostics")
def diagnostics():
    # When the user hits this route, download the data straight from our mock cloud bucket!
    response = s3.get_object(Bucket=BUCKET_NAME, Key="live_fault_code.txt")
    cloud_data = response["Body"].read().decode("utf-8")
    return f"<h2>📊 Data Retrieved From Cloud Bucket:</h2><p>{cloud_data}</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
