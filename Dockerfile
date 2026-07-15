# 1. Usar una imagen base oficial de OpenResty (Nginx + Lua) sobre Alpine Linux (Liviana y segura)
FROM openresty/openresty:1.25.3.1-alpine

# 2. Crear los directorios necesarios dentro del contenedor para tu configuración y scripts
RUN mkdir -p /usr/local/openresty/nginx/conf/ /usr/local/openresty/nginx/lua/

# 3. Copiar tu archivo de configuración de Nginx optimizado al contenedor
# Nota: Ajusta estas rutas si los nombres exactos de tus carpetas locales varían
COPY optimizacion_de_servidor/Alta_optimizacion/conf/nginx.conf /usr/local/openresty/nginx/conf/nginx.conf

# 4. Copiar tus scripts de Lua afinados al contenedor
COPY optimizacion_de_servidor/Alta_optimizacion/lua/ /usr/local/openresty/nginx/lua/

# 5. Exponer el puerto 80 para el tráfico web del API Gateway
EXPOSE 80

# 6. Arrancar Nginx en primer plano para que el contenedor se mantenga vivo corriendo el servicio
CMD ["bin/openresty", "-g", "daemon off;"]
