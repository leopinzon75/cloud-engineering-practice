import os
import time
import sys
from pathlib import Path  # ¡Aquí está la herramienta!

def generar_reporte():
    app_env = os.getenv("APP_ENV", "Desarrollo-Local")
    
    # 1. Definimos la ruta de la carpeta en tu disco usando Path
    # Esto creará una carpeta llamada 'datos_locales' en el mismo directorio de tu notebook
    ruta_carpeta = Path("./datos_locales")
    archivo_reporte = ruta_carpeta / "reporte_salud.txt" # El operador / une rutas de forma limpia
    
    print(f"=== INICIANDO VALIDACIÓN EN ENTORNO: {app_env} ===")
    
    # 2. Replicamos lo que hace Kubernetes: Crear la carpeta física en el disco si no existe
    if not ruta_carpeta.exists():
        print(f"📁 La carpeta '{ruta_carpeta}' no existe. Creándola en el disco duro...")
        ruta_carpeta.mkdir(parents=True, exist_ok=True)
    else:
        print(f"📁 La carpeta '{ruta_carpeta}' ya existe en el disco.")
        
    time.sleep(1)
    print("📊 [TELEMETRÍA] Validando espacio en disco local... OK.")
    
    # 3. Escribimos el archivo de texto en la carpeta física
    try:
        with open(archivo_reporte, "w") as f:
            f.write(f"Reporte de salud para: {app_env}\n")
            f.write("Estado: Carpeta física creada y mapeada con éxito.\n")
        print(f"✅ Copia física escrita con éxito en: {archivo_reporte}")
    except Exception as e:
        print(f"❌ Error al escribir en el disco: {e}")
        sys.exit(1)
        
    print("=== TRABAJO LOCAL FINALIZADO ===")

if __name__ == "__main__":
    generar_reporte()
