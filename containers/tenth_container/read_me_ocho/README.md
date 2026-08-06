# Multi-Cloud Telemetry Simulator (Read Me Ocho)

Este servicio simula el procesamiento e ingesta de telemetría vehicular en un entorno híbrido multi-nube (AWS S3 + Azure Blob Storage) utilizando conectores simulados en memoria (`moto` y Mocks customizados).

## 🏗 Blueprint Architecture Scope
- **Fase:** Architect Python Batch — Módulo Multi-Cloud
- **Input:** Generación automática de 1,000 registros sintéticos en `fleet_data/raw_fleet_telemetry.csv`.
- **AWS Simulator:** `boto3` + `moto[s3]` creando el bucket `fleet-raw-data`.
- **Azure Simulator:** Mock de `BlobServiceClient` para el contenedor `fleet-clean-alerts`.

## 🚀 Despliegue e Integración
```bash
# Pull de la imagen desde Docker Hub
docker pull <TU_USUARIO_DOCKERHUB>/multicloud-telemetry-processor:latest

# Ejecución del contenedor
docker run --rm <TU_USUARIO_DOCKERHUB>/multicloud-telemetry-processor:latest
