from flask import Flask
import boto3
from moto import mock_aws
import os

app = Flask(__name__)

# Initialize mock cloud storage
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
    <a href="/diagnostics" style="padding: 10px 15px; background-color: #007bff; color: black; text-decoration: none; border-radius: 5px; font-family: sans-serif;">
        🚀 Launch System Diagnostics Scanner & Path Analysis
    </a>
    '''

@app.route("/diagnostics")
def diagnostics():
    # 1. Fetch cloud data
    response = s3.get_object(Bucket=BUCKET_NAME, Key="live_fault_code.txt")
    cloud_data = response["Body"].read().decode("utf-8")
     
    # 2. PATH PRACTICE BLOCK (os.path.join & os.path.abspath)
    log_dir_name = "logs"
    file_name = "app_status.txt"
    
    # Safely combine variables into a system path
    relative_file_path = os.path.join(log_dir_name, file_name)
    
    # Calculate absolute system targets
    absolute_file_path = os.path.abspath(relative_file_path)
    absolute_dir_path = os.path.abspath(log_dir_name)
    
    # Get the location of the running script itself
    script_location = os.path.abspath(__file__)
    
    # 3. 🛠️ THE UPGRADE: Replaced the 3-line 'if' block with a single safety net
    os.makedirs(absolute_dir_path, exist_ok=True)
        
    # 4. Write the file out to the hard drive
    status_payload = f"System Scan verified by script at {script_location}. Cloud Message: {cloud_data}"
    with open(absolute_file_path, "w") as f:
        f.write(status_payload)
        
    return f'''
    <h2>📊 System Scan & Path Diagnostics</h2>
    
    <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 5px; font-family: monospace; margin-bottom: 15px;">
        <h3>🔍 Environment Path Metrics:</h3>
        <p><strong>1. Active Script Location (__file__): script_location</strong><br> <span style="color: #d63384;">{script_location}</span></p>
        <p><strong>2. Combined Target Folder Path: absolute_dir_path</strong><br> <span style="color: #0d6efd;">{absolute_dir_path}</span></p>
        <p><strong>3. Final Absolute File Path: absolute_file_path</strong><br> <span style="color: #198754;">{absolute_file_path}</span></p>
    </div>

    <div style="padding: 15px; background-color: #e2f0d9; color: #385723; border: 1px solid #c5e0b4; border-radius: 5px; font-family: monospace; margin-bottom: 15px;">
        📝 <strong>Written File Payload Content: status_payload</strong><br>
        <i>"{status_payload}"</i>
    </div>
    
    <a href="/" style="color: #6c757d; font-family: sans-serif;">⬅️ Return to Main Terminal</a>
    '''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
