from pathlib import Path

# Buscamos la ruta interna del contenedor
CARPETA_LOGS = Path.cwd() / "logs_basicos"
CARPETA_LOGS.mkdir(exist_ok=True)

archivo_salida = CARPETA_LOGS / "hola_mundo.txt"

# Escribimos el archivo de texto
with open(archivo_salida, "w", encoding="utf-8") as file:
    file.write("¡Contenedor básico ejecutado con éxito!\n")

print(f"✅ Archivo creado dentro del contenedor en: {archivo_salida}")
