#!/usr/bin/env bash
# =============================================================================
# monitor-deploy.sh  -  CHẠY TRÊN VM MONITOR (nơi có Docker + stack /opt/monitoring)
#
# Việc script làm (install):
#   1. Kiểm tra file env của Exporter (bắt lỗi http://http://, thiếu khóa) và RGW có với tới được không.
#   2. Chạy (tạo lại) container rgw-usage-exporter, chờ có metric.
#   3. Thêm job rgw-usage + rule_files vào prometheus.yml, thêm volume rules vào docker-compose.yml
#      (có backup, kiểm tra bằng promtool, tự khôi phục nếu lỗi).
#   4. Chép luật cảnh báo, reload Prometheus.
#   5. Import dashboard vào Grafana (nếu có GRAFANA_PASSWORD).
#   6. Chạy bộ kiểm tra cuối.
#
# Cách dùng:
#   GRAFANA_PASSWORD='***' bash monitor-deploy.sh install --env-file /tmp/rgw-exporter.env --site lab
#   bash monitor-deploy.sh check                 # chỉ kiểm tra, không đổi gì
#   GRAFANA_PASSWORD='***' bash monitor-deploy.sh import-dashboard
#
# Cần đặt cạnh script: rgw-usage-alerts.yml và rgw-usage-dashboard.json
# Biến môi trường chỉnh được: BASE_DIR, EXPORTER_DIR, EXPORTER_IMAGE, EXPORTER_PORT,
#   SITE_LABEL, HOST_IP, PROM_URL, PROM_CONTAINER, GRAFANA_URL, GRAFANA_USER, GRAFANA_PASSWORD
# =============================================================================
set -euo pipefail

BASE_DIR="${BASE_DIR:-/opt/monitoring}"
EXPORTER_DIR="${EXPORTER_DIR:-/opt/rgw-exporter}"
EXPORTER_NAME="${EXPORTER_NAME:-rgw-usage-exporter}"
EXPORTER_IMAGE="${EXPORTER_IMAGE:-blemmenes/radosgw_usage_exporter:latest}"
EXPORTER_PORT="${EXPORTER_PORT:-9242}"
SITE_LABEL="${SITE_LABEL:-lab}"
HOST_IP="${HOST_IP:-}"
PROM_URL="${PROM_URL:-http://localhost:9090}"
PROM_CONTAINER="${PROM_CONTAINER:-prometheus}"
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
GRAFANA_USER="${GRAFANA_USER:-admin}"
GRAFANA_PASSWORD="${GRAFANA_PASSWORD:-}"
DASH_UID="rgw-usage-ops"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RULES_SRC="${RULES_SRC:-$SCRIPT_DIR/rgw-usage-alerts.yml}"
DASH_SRC="${DASH_SRC:-$SCRIPT_DIR/rgw-usage-dashboard.json}"
ENV_SRC=""
CMD="install"
TS="$(date +%Y%m%d-%H%M%S)"
PASS=0; FAIL=0; WARNS=0

log()  { printf '\033[1;34m[*]\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m[OK]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m[LỖI]\033[0m %s\n' "$*" >&2; exit 1; }
pass() { PASS=$((PASS+1)); ok "$*"; }
fail() { FAIL=$((FAIL+1)); printf '\033[1;31m[FAIL]\033[0m %s\n' "$*"; }
soft() { WARNS=$((WARNS+1)); warn "$*"; }

get_env() { grep -E "^$2=" "$1" | tail -1 | cut -d= -f2- || true; }

compose() {
  if docker compose version >/dev/null 2>&1; then (cd "$BASE_DIR" && docker compose "$@")
  elif command -v docker-compose >/dev/null 2>&1; then (cd "$BASE_DIR" && docker-compose "$@")
  else die "Không có docker compose."; fi
}

wait_for() {  # wait_for <giây> <mô tả> <lệnh...>
  local n="$1" desc="$2"; shift 2
  local i
  for ((i=0; i<n; i+=3)); do "$@" >/dev/null 2>&1 && return 0; sleep 3; done
  warn "Hết thời gian chờ: $desc"; return 1
}

# ---------------------------------------------------------------- preflight
preflight() {
  [[ $EUID -eq 0 ]] || die "Hãy chạy bằng root."
  for c in docker curl python3; do command -v "$c" >/dev/null || die "Thiếu lệnh '$c'."; done
  [[ -f "$BASE_DIR/docker-compose.yml" ]] || die "Không thấy $BASE_DIR/docker-compose.yml (đã chạy setup-monitoring.sh chưa?)."
  [[ -f "$BASE_DIR/prometheus/prometheus.yml" ]] || die "Không thấy $BASE_DIR/prometheus/prometheus.yml."
  if [[ "$CMD" != "check" ]]; then
    [[ -f "$RULES_SRC" ]] || die "Thiếu file luật: $RULES_SRC"
    [[ -f "$DASH_SRC" ]]  || die "Thiếu file dashboard: $DASH_SRC"
  fi
  [[ -n "$HOST_IP" ]] || HOST_IP="$(hostname -I | awk '{print $1}')"
  ok "Môi trường hợp lệ (VM IP: $HOST_IP)."
}

# ---------------------------------------------------------------- exporter
install_env_file() {
  mkdir -p "$EXPORTER_DIR"; chmod 700 "$EXPORTER_DIR"
  local dst="$EXPORTER_DIR/env" src=""
  if [[ -n "$ENV_SRC" ]]; then src="$ENV_SRC"
  elif [[ -f "$dst" ]]; then src="$dst"
  elif [[ -f /tmp/rgw-exporter.env ]]; then src=/tmp/rgw-exporter.env
  else die "Chưa có file env. Chạy s3gw-prepare.sh trên S3-GW rồi scp sang, sau đó dùng --env-file <đường dẫn>."; fi
  [[ -f "$src" ]] || die "Không thấy file env: $src"
  validate_env "$src"
  if [[ "$src" != "$dst" ]]; then
    [[ -f "$dst" ]] && cp -p "$dst" "$dst.bak-$TS"
    install -m 600 "$src" "$dst"
    ok "Đã cài file env vào $dst (quyền 600)."
  else
    chmod 600 "$dst"; ok "Dùng file env hiện có $dst."
  fi
}

validate_env() {
  local f="$1" srv ak sk
  [[ $(<"$f") != *$'\r'* ]] || die "File env có ký tự CRLF (soạn trên Windows?). Sửa: sed -i 's/\r\$//' $f"
  ! grep -Eq "^[A-Z_]+=[\"']" "$f" || die "File env có giá trị nằm trong dấu nháy; docker --env-file giữ nguyên dấu nháy nên Exporter sẽ đọc sai. Bỏ dấu nháy trong $f"
  srv="$(get_env "$f" RADOSGW_SERVER)"; ak="$(get_env "$f" ACCESS_KEY)"; sk="$(get_env "$f" SECRET_KEY)"
  [[ "$srv" != *"://http"* ]] || die "RADOSGW_SERVER bị lặp 'http://': '$srv' (lỗi đã từng gặp, sửa thành http://IP:CỔNG)."
  [[ "$srv" =~ ^https?://[^/]+/?$ ]] || die "RADOSGW_SERVER không hợp lệ: '$srv'"
  [[ -n "$ak" && -n "$sk" ]] || die "Thiếu ACCESS_KEY/SECRET_KEY trong $f"
  [[ "$srv" != *"$HOST_IP"* ]] || warn "RADOSGW_SERVER trỏ về chính VM monitor? Hãy chắc đây là địa chỉ RGW."
  local code
  code="$(curl -s -o /dev/null -m 6 -w '%{http_code}' "$srv" || true)"
  [[ "$code" != "000" && -n "$code" ]] || die "VM không kết nối được tới RGW $srv (kiểm tra mạng/tường lửa/cổng)."
  ok "RGW $srv trả về HTTP $code (với tới được)."
}

run_exporter() {
  local inner; inner="$(get_env "$EXPORTER_DIR/env" VIRTUAL_PORT)"; inner="${inner:-9242}"
  log "Tạo lại container $EXPORTER_NAME (biến môi trường chỉ nạp lúc tạo container)..."
  docker rm -f "$EXPORTER_NAME" >/dev/null 2>&1 || true
  docker run -d --name "$EXPORTER_NAME" --restart always \
    -p "${EXPORTER_PORT}:${inner}" --env-file "$EXPORTER_DIR/env" "$EXPORTER_IMAGE" >/dev/null
  if wait_for 60 "exporter có metric" bash -c "curl -s -m 5 http://localhost:${EXPORTER_PORT}/metrics | grep -q '^radosgw_usage'"; then
    ok "Exporter đã có metric radosgw_usage_* tại :${EXPORTER_PORT}/metrics"
  else
    docker logs --tail 20 "$EXPORTER_NAME" 2>&1 | sed 's/^/    | /' || true
    die "Exporter chưa trả metric. Xem log phía trên (403 = sai khóa/thiếu quyền; Failed to resolve = sai địa chỉ)."
  fi
}

# ---------------------------------------------------------------- prometheus
edit_compose() {  # in "changed"/"unchanged"
  local f="$BASE_DIR/docker-compose.yml"
  if grep -q 'prometheus/rules:/etc/prometheus/rules' "$f"; then echo unchanged; return; fi
  cp -p "$f" "$f.bak-$TS"
  # Chèn ngay sau dòng volume prometheus.yml, dùng đúng thụt lề của dòng đó (compose có thể thụt 4 hoặc 6 dấu cách).
  sed -i -E 's#^([[:space:]]*)- (\./prometheus/prometheus\.yml:/etc/prometheus/prometheus\.yml(:ro)?)[[:space:]]*$#&\n\1- ./prometheus/rules:/etc/prometheus/rules:ro#' "$f"
  grep -q 'prometheus/rules:/etc/prometheus/rules' "$f" || { cp -p "$f.bak-$TS" "$f"; die "Không tự sửa được docker-compose.yml. Thêm tay dòng '- ./prometheus/rules:/etc/prometheus/rules:ro' vào volumes của prometheus."; }
  echo changed
}

edit_prom_yml() {  # in "changed"/"unchanged"
  local f="$BASE_DIR/prometheus/prometheus.yml"
  cp -p "$f" "$f.bak-$TS.tmp"
  local res
  res="$(python3 - "$f" "$SITE_LABEL" "${HOST_IP}:${EXPORTER_PORT}" <<'PY'
import re, sys
path, site, target = sys.argv[1:4]
txt = open(path).read()
live = re.sub(r'(?m)^\s*#.*$', '', txt)
changed = False
if not re.search(r'(?m)^rule_files:', live):
    m = re.search(r'(?m)^scrape_configs:', txt)
    if not m:
        print("ERR: không thấy mục scrape_configs:"); sys.exit(2)
    txt = txt[:m.start()] + "rule_files:\n  - /etc/prometheus/rules/*.yml\n\n" + txt[m.start():]
    changed = True
job = re.search(r'(?m)^(\s*)-\s*job_name:\s*[\'"]?rgw-usage[\'"]?\s*$', live)
if job:
    # Job đã có (có thể sửa tay từ trước): giữ nguyên, chỉ cảnh báo nếu target khác target mong đợi.
    nxt = re.search(r'(?m)^%s-\s*job_name:' % re.escape(job.group(1)), live[job.end():])
    block = live[job.end():job.end() + nxt.start()] if nxt else live[job.end():]
    if target not in block:
        found = ", ".join(re.findall(r'[\w.-]+:\d+', block)) or "?"
        sys.stderr.write("[!] Job rgw-usage đã có nhưng target là %s, không phải %s. Script không tự sửa job có sẵn: "
                         "sửa tay trong prometheus.yml rồi reload (xem mục 7.6 trong tài liệu).\n" % (found, target))
else:
    keys = re.findall(r'(?m)^([A-Za-z_]+):', live)
    if not keys or keys[-1] != 'scrape_configs':
        print("ERR: scrape_configs không phải mục cuối file, hãy thêm job rgw-usage bằng tay"); sys.exit(2)
    # Dùng cùng thụt lề với các job có sẵn: các phần tử của một danh sách YAML lệch cột là lỗi cú pháp.
    m = re.search(r'(?m)^(\s*)-\s*job_name:', live)
    ind = m.group(1) if m else "  "
    if not txt.endswith("\n"): txt += "\n"
    txt += (
        "\n{i}- job_name: rgw-usage\n"
        "{i}  scrape_interval: 60s\n"
        "{i}  static_configs:\n"
        "{i}    - targets: ['{t}']\n"
        "{i}      labels:\n"
        "{i}        site: '{s}'\n").format(i=ind, t=target, s=site)
    changed = True
if changed: open(path, "w").write(txt)
print("changed" if changed else "unchanged")
PY
)" || { cp -p "$f.bak-$TS.tmp" "$f"; rm -f "$f.bak-$TS.tmp"; die "Sửa prometheus.yml thất bại: $res"; }
  if [[ "$res" == "changed" ]]; then mv "$f.bak-$TS.tmp" "$f.bak-$TS"; else rm -f "$f.bak-$TS.tmp"; fi
  echo "$res"
}

restore_backups() {
  local f
  for f in "$BASE_DIR/docker-compose.yml" "$BASE_DIR/prometheus/prometheus.yml"; do
    [[ -f "$f.bak-$TS" ]] && cp -p "$f.bak-$TS" "$f" && warn "Đã khôi phục $f từ bản backup."
  done
}

setup_prometheus() {
  log "Cấu hình Prometheus (job rgw-usage, luật cảnh báo)..."
  local c1 c2
  c1="$(edit_compose)"; c2="$(edit_prom_yml)"
  mkdir -p "$BASE_DIR/prometheus/rules"
  install -m 644 "$RULES_SRC" "$BASE_DIR/prometheus/rules/rgw-usage-alerts.yml"
  ok "compose: $c1 | prometheus.yml: $c2 | đã chép rgw-usage-alerts.yml"
  log "Áp dụng (docker compose up -d)..."
  compose up -d >/dev/null || { restore_backups; compose up -d >/dev/null || true; die "docker compose up lỗi sau khi sửa cấu hình, đã khôi phục file cũ."; }
  wait_for 60 "Prometheus sẵn sàng" curl -sf "$PROM_URL/-/ready" || { restore_backups; compose up -d >/dev/null || true; die "Prometheus không lên sau khi sửa cấu hình."; }
  if docker exec "$PROM_CONTAINER" promtool check config /etc/prometheus/prometheus.yml >/tmp/promtool.out 2>&1 \
     && docker exec "$PROM_CONTAINER" promtool check rules /etc/prometheus/rules/rgw-usage-alerts.yml >>/tmp/promtool.out 2>&1; then
    ok "promtool: cấu hình và luật hợp lệ."
  else
    sed 's/^/    | /' /tmp/promtool.out; restore_backups; compose up -d >/dev/null || true
    die "promtool báo lỗi, đã khôi phục cấu hình cũ."
  fi
  if curl -sf -X POST "$PROM_URL/-/reload" >/dev/null; then ok "Đã reload Prometheus."
  else warn "Không reload được qua API (thiếu --web.enable-lifecycle?). Dùng: docker restart $PROM_CONTAINER"; fi
}

# ---------------------------------------------------------------- grafana
import_dashboard() {
  [[ -n "$GRAFANA_PASSWORD" ]] || { warn "Chưa có GRAFANA_PASSWORD, bỏ qua import. Import tay: Dashboards > New > Import > chọn $DASH_SRC"; return 0; }
  log "Import dashboard vào Grafana..."
  wait_for 60 "Grafana sẵn sàng" bash -c "curl -s -m 5 '$GRAFANA_URL/api/health' | grep -Eq '\"database\": ?\"ok\"'" \
    || die "Grafana chưa sẵn sàng tại $GRAFANA_URL"
  local payload resp
  payload="$(mktemp)"
  python3 - "$DASH_SRC" > "$payload" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); d.pop("id", None)
print(json.dumps({"dashboard": d, "overwrite": True, "message": "import by monitor-deploy.sh"}))
PY
  resp="$(curl -s -m 20 -K <(printf 'user = "%s:%s"\n' "$GRAFANA_USER" "$GRAFANA_PASSWORD") \
          -H 'Content-Type: application/json' -X POST "$GRAFANA_URL/api/dashboards/db" -d @"$payload")"
  rm -f "$payload"
  if grep -q '"status":"success"' <<<"$resp"; then
    ok "Đã import dashboard 'S3 RGW - User Ops' (uid: $DASH_UID): $GRAFANA_URL/d/$DASH_UID"
  else
    die "Import thất bại: $resp (sai user/mật khẩu Grafana?)"
  fi
}

# ---------------------------------------------------------------- check
check_all() {
  PASS=0; FAIL=0; WARNS=0
  log "=== KIỂM TRA ==="
  # 1. container
  if [[ "$(docker inspect -f '{{.State.Running}}' "$EXPORTER_NAME" 2>/dev/null)" == "true" ]]; then pass "Container $EXPORTER_NAME đang chạy"; else fail "Container $EXPORTER_NAME không chạy"; fi
  # 2. env file
  if [[ -f "$EXPORTER_DIR/env" ]]; then
    [[ "$(stat -c %a "$EXPORTER_DIR/env")" == "600" ]] && pass "File env quyền 600" || fail "File env không phải quyền 600 (chmod 600 $EXPORTER_DIR/env)"
  else fail "Không có $EXPORTER_DIR/env"; fi
  # 3. metrics
  local m owners n
  m="$(curl -s -m 8 "http://localhost:${EXPORTER_PORT}/metrics" || true)"
  n="$(grep -c '^radosgw_usage_ops_total' <<<"$m" || true)"
  if [[ "${n:-0}" -gt 0 ]]; then
    owners="$(grep -o '^radosgw_usage_ops_total{[^}]*' <<<"$m" | grep -o 'owner="[^"]*"' | sort -u | cut -d'"' -f2 | paste -sd, -)"
    pass "Exporter có $n series ops. Các owner: ${owners:-?}"
  else fail "Exporter không có metric radosgw_usage_ops_total"; fi
  # 4. prometheus target
  local tj
  tj="$(curl -s -m 8 "$PROM_URL/api/v1/targets" || true)"
  python3 - "$tj" <<'PY' && pass "Prometheus target rgw-usage = UP" || fail "Prometheus target rgw-usage không UP (xem $PROM_URL/targets)"
import json, sys
try:
    t = json.loads(sys.argv[1])["data"]["activeTargets"]
except Exception:
    sys.exit(1)
sys.exit(0 if any(x["labels"].get("job") == "rgw-usage" and x["health"] == "up" for x in t) else 1)
PY
  # 5. rules
  local rj
  rj="$(curl -s -m 8 "$PROM_URL/api/v1/rules" || true)"
  python3 - "$rj" <<'PY' && pass "Prometheus đã nạp nhóm luật rgw-usage (3 luật)" || fail "Chưa nạp đủ luật rgw-usage (xem $PROM_URL/alerts)"
import json, sys
try:
    g = json.loads(sys.argv[1])["data"]["groups"]
except Exception:
    sys.exit(1)
sys.exit(0 if any(x["name"] == "rgw-usage" and len(x["rules"]) == 3 for x in g) else 1)
PY
  # 6. query thật
  local qj
  qj="$(curl -s -m 8 -G "$PROM_URL/api/v1/query" --data-urlencode 'query=sum by (owner) (rate(radosgw_usage_ops_total[5m]))' || true)"
  python3 - "$qj" <<'PY' && pass "Truy vấn ops/s theo owner có dữ liệu" || soft "Truy vấn ops/s chưa có dữ liệu (cần >=2 phút sau khi có lưu lượng; rate() cần 2 lần scrape)"
import json, sys
try:
    r = json.loads(sys.argv[1])["data"]["result"]
except Exception:
    sys.exit(1)
sys.exit(0 if r else 1)
PY
  # 7. grafana
  if curl -s -m 5 "$GRAFANA_URL/api/health" | grep -Eq '"database": ?"ok"'; then
    pass "Grafana hoạt động"
    if [[ -n "$GRAFANA_PASSWORD" ]]; then
      if curl -s -m 8 -K <(printf 'user = "%s:%s"\n' "$GRAFANA_USER" "$GRAFANA_PASSWORD") "$GRAFANA_URL/api/dashboards/uid/$DASH_UID" | grep -q '"uid":"'"$DASH_UID"'"'; then
        pass "Dashboard $DASH_UID có trong Grafana"
      else fail "Không thấy dashboard $DASH_UID (hoặc sai mật khẩu Grafana)"; fi
    else soft "Bỏ qua kiểm tra dashboard (không có GRAFANA_PASSWORD)"; fi
  else fail "Grafana không phản hồi tại $GRAFANA_URL"; fi
  echo
  log "Kết quả: $PASS đạt, $FAIL lỗi, $WARNS cảnh báo."
  [[ $FAIL -eq 0 ]]
}

# ---------------------------------------------------------------- main
usage() { sed -n '2,21p' "$0"; }

main() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      install|check|import-dashboard) CMD="$1" ;;
      --env-file) ENV_SRC="${2:?thiếu đường dẫn}"; shift ;;
      --site)     SITE_LABEL="${2:?thiếu tên site}"; shift ;;
      -h|--help)  usage; exit 0 ;;
      *) die "Tham số không hợp lệ: $1 (xem --help)" ;;
    esac
    shift
  done
  preflight
  case "$CMD" in
    install)
      install_env_file
      run_exporter
      setup_prometheus
      import_dashboard
      check_all || { echo; die "Còn mục lỗi, xem phía trên."; }
      echo; ok "Hoàn tất. Grafana: $GRAFANA_URL/d/$DASH_UID  |  Prometheus: $PROM_URL/alerts" ;;
    check) check_all ;;
    import-dashboard) import_dashboard ;;
  esac
}
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then main "$@"; fi
