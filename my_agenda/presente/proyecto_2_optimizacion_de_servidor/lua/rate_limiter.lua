local dict = ngx.shared.limiter_storage
local client_ip = ngx.var.remote_addr

local BUCKET_CAPACITY = 10
local REFILL_RATE = 2

local tokens_key = client_ip .. ":tokens"
local time_key = client_ip .. ":last_time"
local now = ngx.now()

local tokens, err = dict:get(tokens_key)
local last_time, _ = dict:get(time_key)

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
else
    dict:set(time_key, now)
    ngx.status = ngx.HTTP_TOO_MANY_REQUESTS
    ngx.header.content_type = "application/json; charset=utf-8"
    ngx.say([[{"error": "Too Many Requests", "message": "Limite superado: Trafico bloqueado por el Rate Limiter."}]])
    ngx.exit(ngx.HTTP_TOO_MANY_REQUESTS)
end
