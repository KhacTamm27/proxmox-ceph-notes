#!/usr/bin/env bash
# Build OpenResty kèm nginx-aws-auth-module và nginx-module-vts trên S3-VTS-NGINX (Debian/Ubuntu, chạy bằng root).
# Chạy lại được: thư mục nguồn đã có thì dùng lại.
set -euo pipefail

OPENRESTY_VERSION="${OPENRESTY_VERSION:-1.29.2.1}"
SRC_DIR="${SRC_DIR:-/root}"

apt update
apt install -y build-essential gcc zlib1g zlib1g-dev openssl libpcre3 libpcre3-dev \
  git libssl-dev make libgd-dev libxml2 libxml2-dev uuid-dev libxslt-dev libgeoip-dev wget

cd "$SRC_DIR"
[[ -f "openresty-${OPENRESTY_VERSION}.tar.gz" ]] || wget "https://openresty.org/download/openresty-${OPENRESTY_VERSION}.tar.gz"
[[ -d nginx-aws-auth-module ]] || git clone https://github.com/kaltura/nginx-aws-auth-module
[[ -d nginx-module-vts ]] || git clone https://github.com/vozlt/nginx-module-vts.git

# Dùng đúng một biến phiên bản cho cả wget và tar (tài liệu gốc từng tải 1.29.2.1 nhưng giải nén 1.15.8.3).
tar xzf "openresty-${OPENRESTY_VERSION}.tar.gz"
cd "openresty-${OPENRESTY_VERSION}"
./configure --add-module="$SRC_DIR/nginx-aws-auth-module/" --add-module="$SRC_DIR/nginx-module-vts/" \
  --prefix=/usr/share/nginx \
  --conf-path=/etc/nginx/nginx.conf \
  --http-log-path=/var/log/nginx/access.log \
  --error-log-path=/var/log/nginx/error.log \
  --lock-path=/var/lock/nginx.lock \
  --pid-path=/run/nginx.pid \
  --modules-path=/usr/lib/nginx/modules \
  --http-client-body-temp-path=/var/lib/nginx/body \
  --http-fastcgi-temp-path=/var/lib/nginx/fastcgi \
  --http-proxy-temp-path=/var/lib/nginx/proxy \
  --http-scgi-temp-path=/var/lib/nginx/scgi \
  --http-uwsgi-temp-path=/var/lib/nginx/uwsgi \
  --with-debug \
  --with-pcre-jit \
  --with-http_ssl_module \
  --with-http_stub_status_module \
  --with-http_realip_module \
  --with-http_auth_request_module \
  --with-http_v2_module \
  --with-http_dav_module \
  --with-http_slice_module \
  --with-threads \
  --with-http_addition_module \
  --with-http_geoip_module=dynamic \
  --with-http_gunzip_module \
  --with-http_gzip_static_module \
  --with-http_image_filter_module=dynamic \
  --with-http_sub_module \
  --with-http_xslt_module=dynamic \
  --with-stream=dynamic \
  --with-stream_ssl_module \
  --with-mail=dynamic \
  --with-mail_ssl_module

gmake -j "$(nproc)"
gmake install
ln -sf /usr/share/nginx/bin/openresty /usr/sbin/nginx

# OpenResty không tự tạo các thư mục temp đã khai báo lúc ./configure: thiếu là nginx -t báo mkdir() failed.
mkdir -p /var/lib/nginx/{body,fastcgi,proxy,scgi,uwsgi} /data/cache
chown -R www-data:www-data /var/lib/nginx /data/cache

nginx -v
echo "Xong. Chép nginx.conf, nginx-lua-file.lua, conf.d/*.conf vào /etc/nginx/ và nginx.service vào /etc/systemd/system/, rồi: nginx -t && systemctl daemon-reload && systemctl enable --now nginx"
