# Batch Telemetry Engine with DynamoDB Distributed Locking (Read M Ten)

Procesador batch multi-servicio AWS con control de concurrencia distribuido mediante DynamoDB (`PipelineLockTable`) e inyección opcional de MinIO/S3.

## 🎛️ Variables de Entorno
- `USE_MOCK`: `"true"` (default) para ejecución auto-contenida con Moto. `"false"` para entorno con MinIO y DynamoDB Local.
- `S3_BUCKET_NAME`: Nombre del bucket S3 de origen/destino.

## 🚀 Ejecución en Docker
```bash
docker run --rm <TU_USUARIO_DOCKERHUB>/multicloud-telemetry-processor:v10
