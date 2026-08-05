import os
import sys
from dotenv import load_dotenv

load_dotenv()

def run_batch():
    batch_name = os.getenv("BATCH_NAME", "Lote-Resiliente-Local")
    total_items = int(os.getenv("TOTAL_ITEMS", "5"))
    simular_error = os.getenv("SIMULAR_ERROR", "False").lower() in ("true", "1", "yes")

    print(f"Iniciando ejecucion del lote: {batch_name}")
    processed = 0

    for item in range(1, total_items + 1):
        if simular_error and item == 3:
            print(f"[ERROR] Inyeccion de falla simulada en el item {item}.")
            raise RuntimeError("Falla provocada por SIMULAR_ERROR")
        
        print(f"Procesando item {item}/{total_items}...")
        processed += 1

    return processed

if __name__ == "__main__":
    try:
        run_batch()
    except Exception as e:
        sys.exit(1)
