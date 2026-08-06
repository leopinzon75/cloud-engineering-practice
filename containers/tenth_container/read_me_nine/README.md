# Multi-Cloud Live Enterprise Telemetry Processor (Read Me Nine)

Servicio de procesamiento de telemetria multicloud con soporte para conmutacion dinamica por variables de entorno (`SIMULACION`).

## 🎛️ Variables de Entorno
- `SIMULACION`: `"True"` para prueba liviana en memoria (3 filas), `"False"` para procesamiento Enterprise (1,000 filas con Moto S3).
- `AWS_INPUT_BUCKET`: Nombre del bucket origen S3.
- `AZURE_OUTPUT_CONTAINER`: Nombre del contenedor destino Azure.

## 🚀 Despliegue con Docker
```bash
# Modo Enterprise (Default: 1,000 filas)
docker run --rm <TU_USUARIO_DOCKERHUB>/multicloud-telemetry-processor:v9

# Modo Simulación en Memoria (3 filas)
docker run --rm -e SIMULACION=True <TU_USUARIO_DOCKERHUB>/multicloud-telemetry-processor:v9
