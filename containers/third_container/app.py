from flask import Flask, redirect, url_for
import boto3
from moto import mock_aws
import os
from datetime import datetime
from pathlib import Path  # 1. Importamos Pathlib

app = Flask(__name__)

# Configuración de rutas seguras y locales en tu área de trabajo
BASE_DIR = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
LOG_FOLDER = BASE_DIR / "logs"  # Creará la carpeta 'logs' dentro de tu carpeta actual

# Start AWS Simulation
mock = mock_aws()
mock.start()

s3 = boto3.client("s3", region_name="us-east-1")
BUCKET_NAME = "vehicle-diagnostic-vault"
FILE_NAME = "live_fault_code.txt"

def seed_bucket():
    s3.create_bucket(Bucket=BUCKET_NAME)
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=FILE_NAME,
        Body="🚨 CLOUD DATA: P0171 - System Too Lean (Bank 1)"
    )

seed_bucket()

# --- 1. THE INTERACTIVE COCKPIT (HUMAN INTERFACE) ---
@app.route("/")
def home():
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_NAME)
        cloud_data = response["Body"].read().decode("utf-8")
        status_html = f"<div style='color: red; font-weight: bold;'>{cloud_data}</div>"
        button_html = f"<form action='/clear-dtc' method='POST'><button style='padding: 10px; background-color: orange;'>🔧 Clear DTC (Reset System)</button></form>"
    except Exception:
        status_html = "<div style='color: green; font-weight: bold;'>✅ SYSTEM CLEAR - No Active Fault Codes Found.</div>"
        button_html = f"<form action='/reset-dtc' method='POST'><button style='padding: 10px; background-color: blue; color: white;'>⚡ Reload Fault Code</button></form>"

    log_event("Dashboard Home Page loaded.")

    return f'''
    <html>
        <body style="font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9;">
            <h1>🌐 Moby Bunny Cloud-Diagnostic Cockpit</h1>
            <hr>
            <h3>Current Vehicle System Status:</h3>
            {status_html}
            <br><br>
            {button_html}
            <br><br>
            <p><a href="/diagnostics">👉 Go to Raw Diagnostics Data Page</a></p>
        </body>
    </html>
    '''

# --- 2. THE RAW DIAGNOSTICS PAGE (DATA INTERFACE) ---
@app.route("/diagnostics")
def diagnostics():
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_NAME)
        cloud_data = response["Body"].read().decode("utf-8")
        log_event("Raw Diagnostics Route Access: Data Found.")
        return f'''
        <h2>📊 Data Retrieved From Cloud Bucket:</h2>
        <p>{cloud_data}</p>
        <br>
        <p><a href="/">⬅️ Return to Home Page</a></p>
        '''
    except Exception:
        log_event("Raw Diagnostics Route Access: System Clear.")
        return f'''
        <h2>📊 Data Retrieved From Cloud Bucket:</h2>
        <p>✅ NO ACTIVE FAULT CODES</p>
        <br>
        <p><a href="/">⬅️ Return to Home Page</a></p>
        '''

# --- ACTION ENDPOINTS ---
@app.route("/clear-dtc", methods=["POST"])
def clear_dtc():
    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=FILE_NAME)
        log_event("Action: DTC Cleared from S3 Bucket.")
    except Exception:
        pass
    return redirect(url_for("home"))

@app.route("/reset-dtc", methods=["POST"])
def reset_dtc():
    s3.put_object(Bucket=BUCKET_NAME, Key=FILE_NAME, Body="🚨 CLOUD DATA: P0171 - System Too Lean (Bank 1)")
    log_event("Action: DTC Reloaded into S3 Bucket.")
    return redirect(url_for("home"))

# --- REUSABLE LOCAL CHASSIS LOG VALVE (CORREGIDO) ---
def log_event(message):
    # Crea la carpeta 'logs' de forma segura en tu espacio local
    LOG_FOLDER.mkdir(parents=True, exist_ok=True)
    
    log_file = LOG_FOLDER / "local_chassis_history.txt"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {message}
")

if __name__ == "__main__":
    # Agregamos use_reloader=False para que no choque con Jupyter
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)