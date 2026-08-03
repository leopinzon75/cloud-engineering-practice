import time
import os
import sys

def run_batch():
    batch_name = os.getenv("BATCH_NAME", "Lote-Resiliente")
    total_items = int(os.getenv("TOTAL_ITEMS", "5"))
    simular_error = os.getenv("SIMULAR_ERROR", "False") == "True"
    
    print(f"=== INICIANDO: {batch_name} ===")
    
    for i in range(1, total_items + 1):
        # Provocamos una falla artificial en la iteración 3 si la bandera está activa
        if simular_error and i == 3:
            print("⚠️ [ERROR SIMULADO] El contenedor experimentó una falla crítica en el nodo.")
            sys.exit(1) # Código de salida de error, rompe el contenedor
            
        print(f" -> Procesando elemento {i}/{total_items}...")
        time.sleep(1)
        
    print(f"=== TRABAJO COMPLETADO CON ÉXITO ===")

if __name__ == "__main__":
    run_batch()
