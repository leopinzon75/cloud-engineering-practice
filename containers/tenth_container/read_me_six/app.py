import os
import sys
from dotenv import load_dotenv

load_dotenv()

def run_service():
    service_name = os.getenv("SERVICE_NAME", "Microservicio-Telemetria")
    max_retries = int(os.getenv("MAX_RETRIES", "3"))
    fail_fast = os.getenv("FAIL_FAST", "False").lower() in ("true", "1", "yes")

    print(f"Iniciando servicio: {service_name}")

    for attempt in range(1, max_retries + 1):
        if fail_fast and attempt == 2:
            print(f"[CRITICAL] Falla simulada alcanzada en el intento {attempt}.")
            raise ConnectionError("Falla de conexion inducida")
        
        print(f"Ejecutando intento de conexion {attempt}/{max_retries}...")

    return True

if __name__ == "__main__":
    try:
        run_service()
    except Exception:
        sys.exit(1)
