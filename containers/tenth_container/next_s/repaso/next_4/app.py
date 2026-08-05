from flask import Flask, request
import boto3
import os
from pathlib import Path
from botocore.exceptions import ClientError

app = Flask(__name__)

S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://minio-service:9000")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "minio_admin")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "minio_password")
BUCKET_NAME = "vehicle-diagnostic-vault"

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name="us-east-1"
)

def ensure_bucket_and_seed():
    try:
        s3.head_bucket(Bucket=BUCKET_NAME)
    except ClientError:
        try:
            s3.create_bucket(Bucket=BUCKET_NAME)
        except Exception:
            pass
    
    # Inyectar el archivo de diagnóstico si no existe
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key="live_fault_code.txt")
    except ClientError:
        try:
            report_content = "🚨 CLOUD DATA: P0300 - Random/Multiple Cylinder Misfire Detected"
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key="live_fault_code.txt",
                Body=report_content
            )
        except Exception:
            pass

@app.route("/")
def home():
    return '''
    <h1>🌐 Diagnostic Web Portal Active</h1>
    <p>Welcome to the main station terminal.</p>
    <hr>
    <a href="/diagnostics" style="padding: 10px 15px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; font-family: sans-serif;">
        🚀 Launch System Diagnostics Scanner
    </a>
    <br><br>
    <a href="/report" style="padding: 10px 15px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px; font-family: sans-serif;">
        📝 Submit New Diagnostic Report
    </a>
    '''

@app.route("/diagnostics")
def diagnostics():
    try:
        ensure_bucket_and_seed()
        
        # Petición a MinIO
        response = s3.get_object(Bucket=BUCKET_NAME, Key="live_fault_code.txt")
        cloud_data = response["Body"].read().decode("utf-8")
          
        # Guardar copia local usando Pathlib
        BASE_DIR = Path.cwd()
        output_dir = BASE_DIR / "output"
        output_filepath = output_dir / "live_fault_code.txt"
        
        output_dir.mkdir(parents=True, exist_ok=True)
            
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(cloud_data)
            
        return f'''
        <h2>📊 System Scan Live Feed</h2>
        <div style="padding: 15px; background-color: #e2f0d9; color: #385723; border: 1px solid #c5e0b4; border-radius: 5px; font-family: monospace; font-size: 1.1em; margin-bottom: 15px;">
            ✅ <strong>Cloud Match Verification:</strong> Connected to S3/MinIO bucket successfully (Provisioned by Terraform).
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
    except Exception as e:
        return f'''
        <h2>❌ Error connecting to cloud storage</h2>
        <p style="color: red; font-family: monospace;">{str(e)}</p>
        <br>
        <a href="/" style="color: #6c757d; font-family: sans-serif;">⬅️ Return to Main Terminal</a>
        '''

# --- RUTA NUEVA: ESCRITURA DUAL (NUBE + DISCO LOCAL) ---
@app.route("/report", methods=["GET", "POST"])
def new_report():
    if request.method == "POST":
        fault_code = request.form.get("code", "P0000 - General Fault")
        vehicle_id = request.form.get("vehicle", "VIN-UNKNOWN")
        
        content = f"🚨 CUSTOM DIAGNOSTIC [{vehicle_id}]: {fault_code}"
        file_key = f"fault_{vehicle_id}.txt"
        
        try:
            ensure_bucket_and_seed()
            
            # 1. Guardar en MinIO (Nube)
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=file_key,
                Body=content
            )
            
            # 2. Guardar copia local con Pathlib (Disco)
            BASE_DIR = Path.cwd()
            output_filepath = BASE_DIR / "output" / file_key
            output_filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_filepath, "w", encoding="utf-8") as f:
                f.write(content)
                
            return f'''
            <h2>✅ Report Saved Successfully</h2>
            <p style="font-family: monospace;"><strong>S3 Object Key:</strong> {file_key}</p>
            <p style="font-family: monospace;"><strong>Local Path:</strong> {output_filepath}</p>
            <hr>
            <a href="/" style="color: #007bff; font-family: sans-serif;">⬅️ Return to Main Terminal</a>
            '''
        except Exception as e:
            return f'''
            <h2>❌ Error Saving Report</h2>
            <p style="color: red; font-family: monospace;">{str(e)}</p>
            <br>
            <a href="/report" style="color: #6c757d; font-family: sans-serif;">⬅️ Try Again</a>
            '''
        
    return '''
    <h2>📝 Submit New Diagnostic Data</h2>
    <form method="POST" style="font-family: sans-serif;">
        <label>Fault Code:</label><br>
        <input type="text" name="code" value="P0171 - System Too Lean" style="width: 300px; padding: 5px;"><br><br>
        <label>Vehicle ID / VIN:</label><br>
        <input type="text" name="vehicle" value="VIN-98765" style="width: 300px; padding: 5px;"><br><br>
        <button type="submit" style="padding: 10px 15px; background-color: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer;">
            🚀 Write to Cloud & Local Storage
        </button>
    </form>
    <br>
    <a href="/" style="color: #6c757d; font-family: sans-serif;">⬅️ Return to Main Terminal</a>
    '''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
