FROM openresty/openresty:alpine

RUN mkdir -p /usr/local/openresty/nginx/lua

COPY conf/nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
COPY lua/rate_limiter.lua /usr/local/openresty/nginx/lua/rate_limiter.lua

EXPOSE 8080

CMD ["/usr/local/openresty/bin/openresty", "-g", "daemon off;"]
