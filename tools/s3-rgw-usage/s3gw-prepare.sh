#!/usr/bin/env bash
# =============================================================================
# s3gw-prepare.sh  -  CHẠY TRÊN NODE S3-GW (node có lệnh radosgw-admin), user root
#
# Việc script làm:
#   1. Kiểm tra usage log của RGW đã có dữ liệu chưa, nếu chưa thì bật.
#   2. Tạo user chỉ-đọc cho Exporter (usage-exporter) với đúng quyền (caps).
#   3. (Tuỳ chọn) Tạo user test-ops để tạo lưu lượng thử.
#   4. Ghi file env cho Exporter vào /root/rgw-exporter.env (quyền 600).
#
# Cách dùng:
#   bash s3gw-prepare.sh                       # chỉ tạo user Exporter + file env
#   bash s3gw-prepare.sh --with-test-user      # tạo thêm user test-ops
#   bash s3gw-prepare.sh --rgw-url http://192.168.69.190:8080
#   bash s3gw-prepare.sh -y                    # tự đồng ý restart RGW nếu cần
#   EXPORTER_ACCESS_KEY=<khóa> bash s3gw-prepare.sh   # chọn khóa khi user exporter có nhiều khóa
#   MONITOR_HOST=<IP VM monitor>               # IP in trong hướng dẫn cuối (mặc định 192.168.69.172)
#
# Script chạy lại nhiều lần được (idempotent). Khóa bí mật KHÔNG in ra màn hình,
# chỉ nằm trong file quyền 600.
# =============================================================================
set -euo pipefail

EXPORTER_UID="${EXPORTER_UID:-usage-exporter}"
TEST_UID="${TEST_UID:-test-ops}"
RGW_URL="${RGW_URL:-}"
OUT_DIR="${OUT_DIR:-/root}"
MONITOR_HOST="${MONITOR_HOST:-192.168.69.172}"
EXPORTER_ACCESS_KEY="${EXPORTER_ACCESS_KEY:-}"   # chọn khóa cụ thể khi user có nhiều khóa (đang xoay khóa)
EXPORTER_CAPS="buckets=read;users=read;usage=read;metadata=read;info=read"
WITH_TEST_USER=0
ASSUME_YES=0

log()  { printf '\033[1;34m[*]\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m[OK]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m[LỖI]\033[0m %s\n' "$*" >&2; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-test-user) WITH_TEST_USER=1 ;;
    --rgw-url)        RGW_URL="${2:?thiếu giá trị cho --rgw-url}"; shift ;;
    -y|--yes)         ASSUME_YES=1 ;;
    -h|--help)        sed -n '2,21p' "$0"; exit 0 ;;
    *) die "Tham số không hợp lệ: $1 (xem --help)" ;;
  esac
  shift
done

# json_get <json> <python-expr>  ví dụ: json_get "$j" 'd["keys"][0]["access_key"]'
json_get() { printf '%s' "$1" | python3 -c "import sys,json; d=json.load(sys.stdin); print($2)"; }

preflight() {
  [[ $EUID -eq 0 ]] || die "Hãy chạy bằng root."
  command -v radosgw-admin >/dev/null || die "Không thấy radosgw-admin. Đây có phải node S3-GW không?"
  command -v python3 >/dev/null || die "Cần python3 (apt install -y python3)."
  radosgw-admin user list >/dev/null 2>&1 || die "radosgw-admin không chạy được (thiếu keyring/ceph.conf?)."
  ok "Môi trường hợp lệ."
}

detect_rgw_url() {
  if [[ -z "$RGW_URL" ]]; then
    local port ip scheme="http"
    port="$(ss -ltnp 2>/dev/null | awk '/radosgw/ {n=split($4,a,":"); print a[n]; exit}')"
    ip="$(hostname -I | awk '{print $1}')"
    [[ -n "$port" ]] || die "Không tự tìm được cổng RGW. Chạy lại với --rgw-url http://IP:CỔNG"
    [[ "$port" == "443" ]] && scheme="https"
    RGW_URL="${scheme}://${ip}:${port}"
  fi
  [[ "$RGW_URL" =~ ^https?://[^/]+$ ]] || die "RGW_URL không hợp lệ: '$RGW_URL' (ví dụ http://192.168.69.190:8080, không có dấu / ở cuối)."
  [[ "$RGW_URL" != *"://http"* ]] || die "RGW_URL bị lặp http:// : '$RGW_URL'"
  ok "Địa chỉ RGW: $RGW_URL"
}

usage_has_data() {
  radosgw-admin usage show 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); sys.exit(0 if d.get("entries") else 1)' 2>/dev/null
}

ensure_usage_log() {
  log "Kiểm tra usage log..."
  if usage_has_data; then
    ok "Usage log đã có dữ liệu (đang hoạt động), bỏ qua bước bật."
    return
  fi
  warn "Chưa thấy dữ liệu usage. Có thể do chưa bật hoặc chưa có lưu lượng nào."
  if command -v ceph >/dev/null 2>&1; then
    # Đã bật sẵn thì chỉ là chưa có lưu lượng: không đặt lại, không restart RGW vô ích.
    if [[ "$(ceph config get client.rgw rgw_enable_usage_log 2>/dev/null)" == "true" ]]; then
      ok "rgw_enable_usage_log đã là true (client.rgw). Tạo vài thao tác S3 rồi kiểm tra lại: radosgw-admin usage show"
      warn "Nếu RGW đặt cấu hình riêng trong ceph.conf ([client.rgw.<tên>]) thì giá trị đó được ưu tiên, hãy kiểm tra thêm ở đó."
      return
    fi
    ceph config set client.rgw rgw_enable_usage_log true
    ok "Đã đặt rgw_enable_usage_log=true (client.rgw)."
    local svc
    svc="$(systemctl list-units 'ceph-radosgw@*' --no-legend --plain 2>/dev/null | awk '{print $1}' | head -1)"
    if [[ -n "$svc" ]]; then
      local ans="n"
      if [[ $ASSUME_YES -eq 1 ]]; then ans="y"; else read -r -p "Restart $svc để áp dụng? (sẽ ngắt RGW vài giây) [y/N] " ans || ans="n"; fi
      if [[ "$ans" =~ ^[Yy]$ ]]; then systemctl restart "$svc"; ok "Đã restart $svc."; else warn "Chưa restart. Hãy restart RGW sau để cấu hình có hiệu lực."; fi
    else
      warn "Không tìm thấy service ceph-radosgw@*. Hãy tự restart RGW."
    fi
  else
    warn "Node này không có lệnh 'ceph'. Thêm thủ công vào ceph.conf, mục [client.rgw.<tên>]:  rgw_enable_usage_log = true  rồi restart RGW."
  fi
}

ensure_user() {  # ensure_user <uid> <display> [caps]  -> in JSON user info ra stdout
  local uid="$1" disp="$2" caps="${3:-}"
  if radosgw-admin user info --uid="$uid" >/dev/null 2>&1; then
    if [[ -n "$caps" ]]; then radosgw-admin caps add --uid="$uid" --caps="$caps" >/dev/null; fi
    radosgw-admin user info --uid="$uid"
  else
    if [[ -n "$caps" ]]; then
      radosgw-admin user create --uid="$uid" --display-name="$disp" --caps="$caps"
    else
      radosgw-admin user create --uid="$uid" --display-name="$disp"
    fi
  fi
}

setup_exporter_user() {
  log "Tạo/kiểm tra user '$EXPORTER_UID' (chỉ đọc)..."
  local j ak sk
  j="$(ensure_user "$EXPORTER_UID" "Usage Exporter" "$EXPORTER_CAPS")"
  # Chỉ lấy khóa S3 của chính user (bỏ khóa subuser). Có nhiều khóa (đang xoay khóa) thì phải chỉ rõ khóa cần dùng.
  local nkeys
  nkeys="$(json_get "$j" 'len([k for k in d["keys"] if k["user"]=="'"$EXPORTER_UID"'"])')"
  if [[ -n "$EXPORTER_ACCESS_KEY" ]]; then
    ak="$EXPORTER_ACCESS_KEY"
  elif [[ "$nkeys" == "1" ]]; then
    ak="$(json_get "$j" '[k for k in d["keys"] if k["user"]=="'"$EXPORTER_UID"'"][0]["access_key"]')"
  else
    die "User $EXPORTER_UID có $nkeys khóa S3. Chạy lại với EXPORTER_ACCESS_KEY=<access key cần dùng> (xem: radosgw-admin user info --uid=$EXPORTER_UID)."
  fi
  sk="$(json_get "$j" 'next((k["secret_key"] for k in d["keys"] if k["access_key"]=="'"$ak"'"), "")')"
  [[ -n "$ak" && -n "$sk" ]] || die "Không lấy được khóa $ak của user $EXPORTER_UID."
  log "Quyền (caps) hiện có của $EXPORTER_UID:"
  json_get "$j" '", ".join(c["type"]+"="+c["perm"] for c in d["caps"])' | sed 's/^/      /'
  local missing=""
  for t in buckets users usage metadata info; do
    json_get "$j" 'any(c["type"]=="'"$t"'" and (c["perm"]=="*" or "read" in c["perm"]) for c in d["caps"])' | grep -q True || missing="$missing $t"
  done
  [[ -z "$missing" ]] || die "Thiếu quyền read cho:$missing"
  ok "Đủ 5 quyền đọc: buckets, users, usage, metadata, info."

  umask 077
  cat > "$OUT_DIR/rgw-exporter.env" <<ENVEOF
RADOSGW_SERVER=$RGW_URL
ADMIN_ENTRY=admin
ACCESS_KEY=$ak
SECRET_KEY=$sk
VIRTUAL_PORT=9242
STORE=default
ENVEOF
  chmod 600 "$OUT_DIR/rgw-exporter.env"
  ok "Đã ghi $OUT_DIR/rgw-exporter.env (quyền 600, có chứa khóa bí mật)."
}

setup_test_user() {
  log "Tạo/kiểm tra user '$TEST_UID' để tạo lưu lượng thử..."
  local j ak sk
  j="$(ensure_user "$TEST_UID" "Test Ops User")"
  ak="$(json_get "$j" 'd["keys"][0]["access_key"]')"
  sk="$(json_get "$j" 'd["keys"][0]["secret_key"]')"
  umask 077
  printf 'user=%s\naccess_key=%s\nsecret_key=%s\nendpoint=%s\n' "$TEST_UID" "$ak" "$sk" "$RGW_URL" > "$OUT_DIR/test-ops-keys.txt"
  chmod 600 "$OUT_DIR/test-ops-keys.txt"
  ok "Khóa user test nằm ở $OUT_DIR/test-ops-keys.txt (dùng nhập vào S3 Browser/aws cli)."
}

summary() {
  cat <<EOM

================ HOÀN TẤT ================
Bước tiếp theo (trên VM monitor $MONITOR_HOST):
  1) Chép file env sang VM monitor:
       scp $OUT_DIR/rgw-exporter.env root@$MONITOR_HOST:/tmp/rgw-exporter.env
  2) Trên VM monitor chạy:
       GRAFANA_PASSWORD='***' bash monitor-deploy.sh install --env-file /tmp/rgw-exporter.env
  3) Xoá file env tạm sau khi xong:
       shred -u /tmp/rgw-exporter.env  (trên VM monitor)
       shred -u $OUT_DIR/rgw-exporter.env  (trên S3-GW, nếu không cần giữ)
==========================================
EOM
}

main() {
  preflight
  detect_rgw_url
  ensure_usage_log
  setup_exporter_user
  [[ $WITH_TEST_USER -eq 1 ]] && setup_test_user
  summary
}
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then main "$@"; fi
