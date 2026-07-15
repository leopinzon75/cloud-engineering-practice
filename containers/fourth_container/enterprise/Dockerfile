# 1. Imagen base oficial de Python liviana
FROM python:3.11-slim

# 2. Configurar variables de entorno para evitar archivos temporales y asegurar logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiar los archivos de configuración e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar el código fuente de la aplicación
COPY pipeline.py .

# 6. Comando por defecto para arrancar la simulación de telemetría
CMD ["python", "pipeline.py"]