import io
import os
from datetime import datetime
import boto3
from azure.storage.blob import BlobServiceClient

def s3_telemetry_streamer(s3_client, bucket, key):
    """Streams records directly out of a live AWS S3 object."""
    response = s3_client.get_object(Bucket=bucket, Key=key)
    s3_data = response["Body"].read().decode("utf-8")
    stream_buffer = io.StringIO(s3_data)
    
    # Skip header
    stream_buffer.readline()
    
    for line in stream_buffer:
        if line.strip():
            row = line.strip().split(",")
            yield {
                "timestamp": row[0],
                "vehicle_id": row[1],
                "engine_rpm": int(row[2]),
                "coolant_temp_c": int(row[3]),
                "fault_code": row[4]
            }

def telemetry_processor(data_entry):
    """Filters out clean records and tags deviations."""
    if data_entry["fault_code"] == "NONE":
        return None
    processed_entry = data_entry.copy()
    processed_entry["alert_status"] = "⚠️ CRITICAL DEVIATION DETECTED"
    processed_entry["processed_at"] = str(datetime.now())
    return processed_entry

def azure_bulk_writer(container_client, blob_name, processed_records):
    """Uploads filtered records directly into an Azure Storage Container."""
    if not processed_records:
        return
    
    csv_buffer = "timestamp,vehicle_id,engine_rpm,coolant_temp_c,fault_code,alert_status,processed_at\n"
    for record in processed_records:
        csv_buffer += (
            f"{record['timestamp']},{record['vehicle_id']},{record['engine_rpm']},"
            f"{record['coolant_temp_c']},{record['fault_code']},{record['alert_status']},\n"
        )
    
    container_client.upload_blob(name=blob_name, data=csv_buffer, overwrite=True)

if __name__ == "__main__":
    print("🚀 Live Enterprise Multi-Cloud Pipeline Booting Up...")
    
    # In production, these secret connection string tokens are pulled safely from Environment Variables
    AWS_BUCKET = os.getenv("AWS_INPUT_BUCKET", "prod-fleet-raw-data")
    AWS_KEY = os.getenv("AWS_INPUT_KEY", "daily_telemetry.csv")
    AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_CONTAINER = os.getenv("AZURE_OUTPUT_CONTAINER", "prod-fleet-alerts")
    
    if not AZURE_CONNECTION_STRING:
        print("❌ Error: Missing AZURE_STORAGE_CONNECTION_STRING environment variable!")
        exit(1)
        
    # Initializing actual cloud clients
    s3 = boto3.client("s3")
    azure_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    azure_container_client = azure_service_client.get_container_client(AZURE_CONTAINER)
    
    print("📥 Connecting to AWS S3 Intake Stream...")
    data_stream = s3_telemetry_streamer(s3, AWS_BUCKET, AWS_KEY)
    
    incidents = []
    for raw_row in data_stream:
        clean_row = telemetry_processor(raw_row)
        if clean_row:
            incidents.append(clean_row)
            
    print(f"📤 Uploading {len(incidents)} processed records to Azure Blob Storage...")
    azure_bulk_writer(azure_container_client, "critical_incidents_report.csv", incidents)
    
    print("🏁 Batch complete! Multi-cloud handoff successful.")
