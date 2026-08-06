# Fleet Telemetry Processor (Read M Seven)

Este servicio simula el flujo de datos de telemetría para una flota vehicular, procesando métricas del motor y filtrando códigos de falla críticos (DTC).

## Lógica del Pipeline
1. Genera 10,000 registros sintéticos en `data/input/raw_fleet_telemetry.csv`.
2. Lee los datos en streaming usando generadores de Python para optimizar memoria.
3. Filtra registros con `fault_code == "NONE"`.
4. Escribe incidentes críticos en `data/output/clean_critical_incidents.csv`.

## Ejecución Local
```bash
python app.py
