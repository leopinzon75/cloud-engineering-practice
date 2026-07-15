from flask import Flask
import boto3
from moto import mock_aws

app = Flask(__name__)

# Start AWS simulation layer in global memory
mock = mock_aws()
mock.start()

# Wire up the Boto3 S3 client to our simulation road
s3 = boto3.client("s3", region_name="us-east-1")
BUCKET_NAME = "vehicle-diagnostic-vault"
s3.create_bucket(Bucket=BUCKET_NAME)

# Seed our cloud bucket with data
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
    # Fetch file object container from mock cloud via Boto3
    response = s3.get_object(Bucket=BUCKET_NAME, Key="live_fault_code.txt")
    # Stream and decode the body dictionary key
    cloud_data = response["Body"].read().decode("utf-8")
    return f"<h2>📊 Data Retrieved From Cloud Bucket:</h2><p>{cloud_data}</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
