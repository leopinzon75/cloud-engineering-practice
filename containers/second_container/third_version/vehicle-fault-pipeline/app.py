from flask import Flask
import boto3
from moto import mock_aws
from pathlib import Path  # <-- Cambiado al estándar moderno

app = Flask(__name__)

mock = mock_aws()
mock.start()

s3 = boto3.client("s3", region_name="us-east-1")
BUCKET_NAME = "vehicle-diagnostic-vault"
s3.create_bucket(Bucket=BUCKET_NAME)

s3.put_object(
    Bucket=BUCKET_NAME,
    Key="live_fault_code.txt",
    Body="🚨 CLOUD DATA: P0171 - System Too Lean (Bank 1)"
)

@app.route("/")
def home():
    return '''
    <h1>🌐 Diagnostic Web Portal Active</h1>
    <p>Welcome to the main station terminal.</p>
    <hr>
    <a href="/diagnostics" style="padding: 10px 15px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; font-family: sans-serif;">
        🚀 Launch System Diagnostics Scanner
    </a>
    '''

@app.route("/diagnostics")
def diagnostics():
    response = s3.get_object(Bucket=BUCKET_NAME, Key="live_fault_code.txt")
    cloud_data = response["Body"].read().decode("utf-8")
     
    # 🎯 SOLUCIÓN CLOUD DINÁMICA: Encuentra la ruta local actual de forma inteligente
    BASE_DIR = Path.cwd()
    output_dir = BASE_DIR / "output"
    output_filepath = output_dir / "live_fault_code.txt"
    
    # Pathlib crea la estructura de forma segura sin importar el Sistema Operativo
    output_dir.mkdir(parents=True, exist_ok=True)
        
    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(cloud_data)
        
    return f'''
    <h2>📊 System Scan Live Feed</h2>
    <div style="padding: 15px; background-color: #e2f0d9; color: #385723; border: 1px solid #c5e0b4; border-radius: 5px; font-family: monospace; font-size: 1.1em; margin-bottom: 15px;">
        ✅ <strong>Cloud Match Verification:</strong> Connected to mock S3 bucket successfully.
    </div>
    <div style="padding: 15px; background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; border-radius: 5px; font-family: monospace; font-size: 1.2em;">
        {cloud_data}
    </div>
    <p style="color: #2e75b6; font-family: sans-serif; font-weight: bold;">
        💾 Local Host Sync: Copy written to path '{output_filepath}'
    </p>
    <br>
    <a href="/" style="color: #6c757d; font-family: sans-serif;">⬅️ Return to Main Terminal</a>
    '''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
