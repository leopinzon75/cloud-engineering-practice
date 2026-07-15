#!/usr/bin/env python3
"""
SISTEMA DE PROCESAMIENTO DE DIAGNÓSTICOS DE FLOTA AUTOMATIZADO
Cliente: Upwork Enterprise Case Study
Desarrollador: Cloud Engineering Specialist

Versión Moderna: Optimizado con Pathlib para ejecución en contenedores.
"""

import sys
from datetime import datetime
from pathlib import Path

# GESTIÓN DINÁMICA DE RUTAS
BASE_DIR = Path.cwd()
INPUT_DIR = BASE_DIR / "data_input"
OUTPUT_DIR = BASE_DIR / "logs"

def inicializar_entorno():
    """Garantiza que la infraestructura de carpetas exista."""
    try:
        INPUT_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        print(f"📡 [ENTORNO] Infraestructura lista con Pathlib dentro del Contenedor.")
    except Exception as e:
        print(f"❌ [ERROR] No se pudieron crear las carpetas: {e}")
        sys.exit(1)

def procesar_diagnosticos_flota():
    """Lee las métricas de la flota y genera un reporte limpio."""
    print("⚡ [PROCESO] Iniciando escaneo de datos operativos...")
    
    datos_crudos_vehiculos = [
        {"id_unidad": "TRUCK-01", "error_code": "P0300", "estado": "Critico"},
        {"id_unidad": "VAN-04", "error_code": "None", "estado": "Operativo"},
        {"id_unidad": "TRUCK-02", "error_code": "P0171", "estado": "Revision"},
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_salida = OUTPUT_DIR / f"reporte_limpio_{timestamp}.txt"
    
    try:
        print(f"✍️ [ESCRITURA] Escribiendo reporte en: {archivo_salida}")
        
        with open(archivo_salida, "w", encoding="utf-8") as file:
            file.write("==================================================\n")
            file.write(f"REPORTE CONSOLIDADO DE REVISIÓN DE FLOTA - {datetime.now()}\n")
            file.write("==================================================\n\n")
            
            unidades_procesadas = 0
            for vehiculo in datos_crudos_vehiculos:
                if vehiculo["error_code"] != "None":
                    linea = f"[ALERTA] Unidad: {vehiculo['id_unidad']} | Código: {vehiculo['error_code']} | Status: {vehiculo['estado']}\n"
                    file.write(linea)
                    unidades_processed = unidades_procesadas + 1
            
            file.write(f"\n[RESUMEN] Procesamiento completado.\n")
            
        print("✅ [ÉXITO] El reporte automatizado se ha generado correctamente.")
        
    except IOError as e:
        print(f"❌ [ERROR] Fallo de entrada/salida: {e}")
    except Exception as e:
        print(f"❌ [ERROR] Error inesperado: {e}")

if __name__ == "__main__":
    print("🚀 --- INICIANDO PIPELINE DE AUTOMATIZACIÓN EN CONTENEDOR ---")
    inicializar_entorno()
    procesar_diagnosticos_flota()
    print("🏁 --- PIPELINE FINALIZADO CON ÉXITO ---")
