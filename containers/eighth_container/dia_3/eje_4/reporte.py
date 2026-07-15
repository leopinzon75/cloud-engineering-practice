import os
import time
import sys
from pathlib import Path

def generar_reporte():
    # 1. Leemos el entorno (por defecto será Desarrollo-Local)
    app_env = os.getenv("APP_ENV", "Desarrollo-Local")
    
    # 2. Definimos la ruta de la carpeta interna donde el script intentará escribir
    ruta_carpeta = Path("/app/datos_reporte")
    archivo_reporte = ruta_carpeta / "reporte_salud.txt"
    
    print(f"=== INICIANDO VALIDACIÓN EN ENTORNO: {app_env} ===")
    
    # 3. Verificamos si la carpeta existe. Si no, la creamos.
    if not ruta_carpeta.exists():
        print(f"📁 La carpeta '{ruta_carpeta}' no existe. Creándola...")
        try:
            ruta_carpeta.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"❌ Error al crear la carpeta en el disco: {e}")
            sys.exit(1)
    else:
        print(f"📁 La carpeta '{ruta_carpeta}' ya existe.")
        
    time.sleep(1)
    
    # 4. Intentamos escribir el archivo de texto con los datos
    try:
        with open(archivo_reporte, "w") as f:
            f.write(f"Reporte de salud para: {app_env}\n")
            f.write("Estado: Conexión de almacenamiento exitosa.\n")
        print(f"✅ Archivo escrito con éxito en: {archivo_reporte}")
    except Exception as e:
        print(f"❌ Error al escribir el archivo: {e}")
        sys.exit(1)
        
    print("=== TRABAJO FINALIZADO ===")

if __name__ == "__main__":
    generar_reporte()
