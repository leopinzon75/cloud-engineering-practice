# 📡 Microservicio de Telemetría & Simulación de Fallas de Red

## 📌 Descripción del Proyecto
Este módulo simula la ejecución de un microservicio enfocado en la recolección de telemetría y validación de resiliencia ante cortes de red. Incorpora un interruptor de entorno (`FAIL_FAST`) diseñado para validar la respuesta del orquestador e iterar dentro de pipelines automatizados de CI/CD.

---

## 🏗️ Configuración de Entorno

| Variable | Descripción | Valor Predeterminado |
| :--- | :--- | :--- |
| `SERVICE_NAME` | Identificador del microservicio | `Microservicio-Telemetria` |
| `MAX_RETRIES` | Reintentos máximos permitidos | `3` |
| `FAIL_FAST` | Simulación de fallo en el intento 2 (`True` / `False`) | `False` |

---

## 🚀 Pruebas y Ejecución Local

```bash
# Ejecutar la aplicación
python app.py

# Ejecutar las pruebas unitarias
pytest test_app.py --verbose
