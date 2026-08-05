import boto3
from moto import mock_aws
from app import app, set_s3_client

# 1. Inicia la nube simulada en memoria
mock = mock_aws()
mock.start()

# 2. Crea e inyecta el cliente simulado
mock_s3 = boto3.client("s3", region_name="us-east-1")
set_s3_client(mock_s3)

print("🚀 Servidor corriendo en http://127.0.0.1:5000 (Modo En Memoria)")

# 3. Arranca el servidor de Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
