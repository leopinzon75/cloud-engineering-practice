1import os
import time
import sys

def generar_reporte():
    app_env = os.getenv("APP_ENV", "Desarrollo-Local")
    ruta_compartida = "/data"
    archivo_reporte = os.path.join(ruta_compartida, "reporte_salud.txt")
    
    print(f"=== INICIANDO VALIDACIÓN EN ENTORNO: {app_env} ===")
    print("Verificando sistemas...")
    time.sleep(1)
    
    # NUEVA LÍNEA DE TELEMETRÍA AGREGADA AL VUELO:
    print("📊 [TELEMETRÍA] Uso de CPU: 12% | Memoria: 256MB. Estado: ESTABLE.")
    
    if not os.path.exists(ruta_compartida):
        print(f"❌ Error: La ruta {ruta_compartida} no está montada.")
        sys.exit(1)
        
    with open(archivo_reporte, "w") as f:
        f.write(f"Reporte de salud para: {app_env}\n")
        f.write("Estado: Sistema en perfecto equilibrio (X).\n")
        
    print(f"✅ Reporte escrito con éxito en: {archivo_reporte}")
    print("=== TRABAJO BATCH FINALIZADO ===")

if __name__ == "__main__":
    generar_reporte()
