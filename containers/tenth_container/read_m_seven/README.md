# Fleet Telemetry Batch Processor — Architect Python Batch (Phase 8/9)

Este servicio procesa lotes (*batch*) de datos de telemetría vehicular, aplicando filtrado y enriquecimiento en memoria mediante generadores de Python para optimizar recursos.

## 🏗 Architecture & Blueprint Scope
- **Fase:** 8 de 9 (CI/CD Pipeline, Documentación GitHub y Registro en Docker Hub).
- **Pattern:** Batch Ingestion & Filtering.
- **Input:** `data/input/raw_fleet_telemetry.csv` (10,000 eventos sintéticos).
- **Output:** `data/output/clean_critical_incidents.csv` (Registro de códigos DTC críticos).

## 🚀 CI/CD & Deployment Pipeline
1. **Testing & Build:** Ejecución de pruebas y compilación automática mediante GitHub Actions.
2. **Registry:** Publicación de la imagen en Docker Hub.
3. **Pull & Execution:** Consumo de la imagen remota verificada.
