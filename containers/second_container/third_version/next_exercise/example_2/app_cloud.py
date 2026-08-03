import boto3
from moto import mock_aws
from pathlib import Path
from datetime import datetime

# 1. Definimos las rutas locales temporales con Pathlib
BASE_DIR = Path.cwd()
LOCAL_LOGS = BASE_DIR / "temp_logs"
LOCAL_LOGS.mkdir(exist_ok=True)

@mock_aws
def ejecutar_pipeline_cloud():
    print("☁️ [AWS] Iniciando entorno virtual simulado de S3...")
    
    # 2. Inicializar el cliente de AWS S3
    s3_client = boto3.client("s3", region_name="us-east-1")
    
    # 3. Crear el "Bucket" (la cubeta de almacenamiento en la nube)
    nombre_bucket = "reportes-flota-enterprise"
    s3_client.create_bucket(Bucket=nombre_bucket)
    print(f"📦 [S3] Bucket '{nombre_bucket}' creado con éxito en AWS Virtual.")
    
    # 4. Crear el reporte localmente primero usando Pathlib
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_local = LOCAL_LOGS / f"diagnostico_{timestamp}.txt"
    
    with open(archivo_local, "w", encoding="utf-8") as file:
        file.write(f"=== REPORTE SUBIDO A AWS S3 ===\n")
        file.write(f"Fecha de ejecución: {datetime.now()}\n")
        file.write(f"Estado de la Flota: Operativa / Sin Errores Críticos.\n")
        
    print(f"✍️ [LOCAL] Reporte temporal creado en: {archivo_local.name}")
    
    # 5. SUBIR EL ARCHIVO A LA NUBE (La prueba de fuego de Boto3)
    # Convertimos la ruta de Pathlib a string porque AWS requiere texto
    nombre_objeto_s3 = f"logs/año=2026/{archivo_local.name}"
    
    s3_client.upload_file(
        Filename=str(archivo_local),
        Bucket=nombre_bucket,
        Key=nombre_objeto_s3
    )
    print(f"🚀 [CLOUD] ¡Archivo subido exitosamente a S3 de AWS! Destino: s3://{nombre_bucket}/{nombre_objeto_s3}")

    # 6. VERIFICACIÓN: Listar los archivos que están en la nube para confirmar
    print("\n🔍 [VERIFICACIÓN] Consultando el Bucket de AWS S3...")
    respuesta = s3_client.list_objects_v2(Bucket=nombre_bucket)
    
    for objeto in respuesta.get("Contents", []):
        print(f"📌 Encontrado en la nube S3 -> Tamaño: {objeto['Size']} bytes | Llave: {objeto['Key']}")

if __name__ == "__main__":
    print("🚀 --- INICIANDO PIPELINE DE AUTOMATIZACIÓN CLOUD ---")
    ejecutar_pipeline_cloud()
    print("🏁 --- PIPELINE CLOUD FINALIZADO CON ÉXITO ---")
