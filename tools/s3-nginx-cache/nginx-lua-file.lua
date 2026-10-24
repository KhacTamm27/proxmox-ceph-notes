-- /etc/nginx/nginx-lua-file.lua
-- Gom các header đã ký (SignedHeaders) và Authorization gốc của client vào biến authvar.
-- NGINX gửi authvar lên RGW trong header X-Amz-Cache để RGW kiểm tra quyền của user gốc
-- khi request được ký lại bằng user aws_cache. Chỉ áp dụng cho GET object có chữ ký SigV4.
local check = ngx.req.get_headers()["AUTHORIZATION"]
local uri =  ngx.var.request_uri
local ngx_re = require "ngx.re"
local hdrs = ngx.req.get_headers()

ngx.var.authvar = ""

if check == nil then
    return
end

local res, err = ngx_re.split(check,"SignedHeaders=")
if not res or not res[2] then return end
local res2, err2 = ngx_re.split(res[2],",")
if not res2 or not res2[1] then return end
local res3, err3 = ngx_re.split(res2[1],";")
if not res3 then return end

local t = {}
local concathdrs = string.char(0x00)
for i = 1, #res3, 1 do
    if hdrs[res3[i]] ~= nil then
        t[i] = res3[i] .. string.char(0xB1) ..  hdrs[res3[i]]
        concathdrs = concathdrs .. string.char(0xB2) .. t[i]
    end
end

local xamzcache = concathdrs:sub(2)
xamzcache = xamzcache .. string.char(0xB2) .. "Authorization" .. string.char(0xB1) .. check
if xamzcache:find("aws4_request") ~= nil and uri ~= "/" and uri:find("?") == nil and hdrs["if-match"] == nil then
    ngx.var.authvar = xamzcache
end
