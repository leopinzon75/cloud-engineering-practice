# ⚙️ Engine de Procesamiento Batch Resiliente & Inyección de Fallas Controladas

## 📌 Descripción del Proyecto
Este proyecto implementa un **motor de procesamiento por lotes (Batch Job)** desacoplado, diseñado para ejecutar tareas secuenciales en segundo plano dentro de entornos containerizados. Incorpora un mecanismo de **inyección de fallas en tiempo de ejecución (Fault Injection)** para validar la resiliencia de la infraestructura, probar políticas de reintento (*restart policies*) y evaluar la estabilidad de pipelines de Integración Continua (CI/CD).

---

## 🏗️ Arquitectura y Componentes
* **Control por Variables de Entorno:** Parametrización dinámica del tamaño del lote (`TOTAL_ITEMS`), nombre del proceso (`BATCH_NAME`) y activación de interrupciones del sistema (`SIMULAR_ERROR`).
* **Manejo Estándar de Exit Codes:** Gestión explícita de señales POSIX mediante `sys.exit(1)` para comunicar fallas críticas al orquestador de contenedores (Docker/Kubernetes) o al ejecutor de GitHub Actions.
* **Tolerancia a Fallas & Testing:** Suite de pruebas automatizadas con `pytest` y `monkeypatch` para simular escenarios de éxito y manejo de excepciones sin modificar el entorno global.

---

## 🛠️ Configuración y Variables de Entorno
El comportamiento del proceso se define a través de un archivo `.env`:

| Variable | Descripción | Valor Predeterminado |
| :--- | :--- | :--- |
| `BATCH_NAME` | Etiqueta para identificar el trabajo | `Lote-Resiliente` |
| `TOTAL_ITEMS` | Número total de iteraciones a procesar | `5` |
| `SIMULAR_ERROR` | Interruptor para forzar un fallo en la iteración 3 (`True` / `False`) | `False` |

---

## 🚀 Guía de Ejecución Local

### 1. Entorno Virtual Python
```bash
# Instalación de dependencias
pip install -r requirements.txt

# Ejecución del trabajo
python app.py
