import os
from flask import Flask
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")
AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "minio_admin")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY", "minio_password")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "vehicle-diagnostic-vault")

# Objeto global s3, modificable para inyección en pruebas
s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=AWS_KEY,
    aws_secret_access_key=AWS_SECRET,
    region_name="us-east-1"
)

def set_s3_client(custom_client):
    """Inyecta un cliente S3 personalizado (útil para moto / mocks)."""
    global s3
    s3 = custom_client

def ensure_bucket_exists():
    try:
        s3.head_bucket(Bucket=BUCKET_NAME)
    except ClientError:
        try:
            s3.create_bucket(Bucket=BUCKET_NAME)
        except Exception:
            pass

@app.route("/")
def home():
    return "🌐 Cloud-Connected Diagnostic Portal Active"

@app.route("/seed")
def seed_data():
    ensure_bucket_exists()
    report_content = "🚨 CLOUD DATA: P0171 - System Too Lean (Bank 1)"
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key="live_fault_code.txt",
        Body=report_content
    )
    return "✅ Seeded fault code P0171 into MinIO S3!"

@app.route("/diagnostics")
def diagnostics():
    try:
        ensure_bucket_exists()
        response = s3.get_object(Bucket=BUCKET_NAME, Key="live_fault_code.txt")
        cloud_data = response["Body"].read().decode("utf-8")
        return f"📊 Data Retrieved From Cloud Bucket: {cloud_data}"
    except s3.exceptions.NoSuchKey:
        return "⚠️ No diagnostic data found yet. Visit /seed first or upload a file to MinIO.", 404
    except Exception as e:
        return f"❌ Error connecting to cloud storage: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port)
