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

# Route 1: The Main Homepage
@app.route("/")
def home():
    return """
    <h1>🌐 Diagnostic Web Portal Active</h1>
    <p>Welcome to the main station terminal.</p>
    <hr>
    <a href="/diagnostics" style="padding: 10px 15px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; font-family: sans-serif;">
        🚀 Launch System Diagnostics Scanner
    </a>
    """

# Route 2: The Diagnostics Scanner Page (Now reading dynamically from Mock S3!)
@app.route("/diagnostics")
def diagnostics():
    response = s3.get_object(Bucket=BUCKET_NAME, Key="live_fault_code.txt")
    cloud_data = response["Body"].read().decode("utf-8")
     
    return f"""
    <h2>📊 System Scan Live Feed</h2>
    <div style="padding: 15px; background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; border-radius: 5px; font-family: monospace; font-size: 1.2em;">
        {cloud_data}
    </div>
    <br><br>
    <a href="/" style="color: #6c757d; font-family: sans-serif;">⬅️ Return to Main Terminal</a>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
