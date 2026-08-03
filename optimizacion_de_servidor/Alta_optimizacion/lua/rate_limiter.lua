local _M = {}

-- La función ahora acepta parámetros dinámicos con valores de respaldo (fallback)
function _M.check_rate(custom_capacity, custom_refill_rate)
    local dict = ngx.shared.limiter_storage
    local client_ip = ngx.var.remote_addr
    
    if not client_ip or client_ip == "" then
        client_ip = "global"
    end
    
    -- Convertimos los parámetros de Nginx (strings) a números de Lua
    local BUCKET_CAPACITY = tonumber(custom_capacity) or 3
    local REFILL_RATE = tonumber(custom_refill_rate) or 1
    
    local tokens_key = client_ip .. ":tokens"
    local time_key = client_ip .. ":last_time"
    local now = ngx.now()
    
    -- Bloque seguro: Si el diccionario falla, atrapamos el error para no tirar el Gateway
    local tokens, err = dict:get(tokens_key)
    local last_time, _ = dict:get(time_key)
    
    if err then
        -- [Opción 3] Fail-safe: Si la RAM da error, dejamos pasar el tráfico por seguridad
        ngx.log(ngx.ERR, "[Gateway] Error leyendo diccionario compartido: ", err)
        return
    end
    
    if not tokens then
        tokens = BUCKET_CAPACITY
        last_time = now
    else
        local time_passed = now - last_time
        local tokens_to_add = time_passed * REFILL_RATE
        tokens = math.min(BUCKET_CAPACITY, tokens + tokens_to_add)
    end
    
    if tokens >= 1 then
        tokens = tokens - 1
        dict:set(tokens_key, tokens)
        dict:set(time_key, now)
        return
    else
        dict:set(time_key, now)
        
        -- [Opción 2] Monitoreo: Registramos el bloqueo con la IP exacta en el log de Nginx
        ngx.log(ngx.WARN, "[Gateway Freno de Mano] IP Bloqueada: ", client_ip, " - Excedió el límite de ", BUCKET_CAPACITY, " reqs.")
        
        ngx.status = ngx.HTTP_TOO_MANY_REQUESTS
        ngx.header.content_type = "application/json; charset=utf-8"
        ngx.say([[{"error": "Too Many Requests", "message": "Freno de mano: Has excedido el límite de velocidad en el Gateway."}]])
        
        return ngx.exit(ngx.HTTP_OK)
    end
end

return _M
