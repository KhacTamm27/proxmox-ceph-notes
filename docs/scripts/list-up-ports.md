# Liệt kê cổng mạng vật lý đang UP (1Gb / 10Gb) trên mọi node cluster

[← Mục lục](../../README.md) · Script tiện ích

**Mục đích:** Kiểm tra nhanh card mạng vật lý nào đang UP và đạt tốc độ nào trên từng node của cluster (đọc danh sách node và IP từ /etc/pve/.members), để phát hiện cổng rớt tốc độ, đứt cáp hoặc cắm nhầm cổng.

## Cách dùng

```bash
./list_up_ports.sh    # Liệt kê cổng UP ở 10Gb và 1Gb (mặc định)
SPEEDS="10000" ./list_up_ports.sh    # Chỉ cổng 10Gb
SPEEDS="1000 10000 25000" ./list_up_ports.sh    # Thêm các mức tốc độ khác (đơn vị Mb/s)
SSH_USER=root SSH_PORT=22 ./list_up_ports.sh    # Đổi user hoặc cổng SSH
```

File gốc: [`tools/list_up_ports.sh`](../../tools/list_up_ports.sh)

## Lưu ý

Chạy trên một node trong cluster; cần SSH bằng key (không mật khẩu) từ node này tới các node còn lại, cluster Proxmox thường đã có sẵn. Chỉ xét cổng vật lý đang UP (có /sys/class/net/TÊN_CỔNG/device) nên bridge, bond, VLAN ảo không hiện. Node offline hoặc SSH lỗi được ghi rõ trong bảng, node không có cổng khớp hiện (none). Card 10Gb mà chỉ báo 1Gb thường do cáp, SFP hoặc cổng switch. Script bật StrictHostKeyChecking=no và UserKnownHostsFile=/dev/null: tiện trong mạng nội bộ nhưng bỏ qua kiểm tra host key. Thiếu python3 trên node chạy thì script dừng.

## Mã nguồn

```bash
#!/usr/bin/env bash
# list_up_ports.sh
# List physical NIC ports that are UP at 10Gb / 1Gb for every node in a Proxmox cluster.
# Hostname and IP are read from /etc/pve/.members.
#
# Usage:
#   ./list_up_ports.sh                 # 10Gb + 1Gb ports (default)
#   SPEEDS="10000" ./list_up_ports.sh  # only 10Gb
#   SPEEDS="1000 10000 25000" ./list_up_ports.sh
#   SSH_USER=root SSH_PORT=22 ./list_up_ports.sh

set -u

MEMBERS="/etc/pve/.members"
SPEEDS="${SPEEDS:-1000 10000}"        # Mb/s values to match
SSH_USER="${SSH_USER:-root}"
SSH_PORT="${SSH_PORT:-22}"
SSH_OPTS=(-o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=no
          -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -p "$SSH_PORT")

[[ -r "$MEMBERS" ]] || { echo "ERROR: cannot read $MEMBERS (not a Proxmox node?)" >&2; exit 1; }
command -v python3 >/dev/null || { echo "ERROR: python3 not found" >&2; exit 1; }

# Remote/local collector: prints "<port> <speed_mbps>" for physical ports with operstate=up
COLLECT='
for p in /sys/class/net/*; do
  n=${p##*/}
  [ -e "$p/device" ] || continue
  [ "$(cat "$p/operstate" 2>/dev/null)" = "up" ] || continue
  s=$(cat "$p/speed" 2>/dev/null) || continue
  echo "$n $s"
done
'

# Parse .members -> "name ip online"
mapfile -t NODES < <(python3 - "$MEMBERS" <<'PY'
import json, sys, re
d = json.load(open(sys.argv[1]))
nl = d.get("nodelist", {})
def key(k):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", k)]
for name in sorted(nl, key=key):
    v = nl[name]
    print(name, v.get("ip", "-"), v.get("online", 0))
PY
)

[[ ${#NODES[@]} -gt 0 ]] || { echo "ERROR: no nodes found in $MEMBERS" >&2; exit 1; }

LOCAL_NAME="$(hostname -s)"
FMT="%-22s %-16s %-14s %-8s\n"

printf "$FMT" "HOST" "IP" "PORT" "SPEED"
printf "$FMT" "----------------------" "----------------" "--------------" "--------"

total=0
for line in "${NODES[@]}"; do
  read -r name ip online <<<"$line"

  if [[ "$online" != "1" ]]; then
    printf "$FMT" "$name" "$ip" "(node offline)" "-"
    continue
  fi

  if [[ "$name" == "$LOCAL_NAME" ]]; then
    out="$(bash -c "$COLLECT" 2>/dev/null)"
  else
    out="$(ssh "${SSH_OPTS[@]}" "${SSH_USER}@${ip}" "$COLLECT" 2>/dev/null)" || {
      printf "$FMT" "$name" "$ip" "(ssh failed)" "-"
      continue
    }
  fi

  found=0
  while read -r port speed; do
    [[ -n "${port:-}" ]] || continue
    for want in $SPEEDS; do
      if [[ "$speed" == "$want" ]]; then
        if (( speed >= 1000 )); then label="$((speed / 1000))Gb"; else label="${speed}Mb"; fi
        printf "$FMT" "$name" "$ip" "$port" "$label"
        found=1; total=$((total + 1))
        break
      fi
    done
  done <<<"$out"

  (( found )) || printf "$FMT" "$name" "$ip" "(none)" "-"
done

echo
echo "Total matching UP ports: $total  (speeds: $SPEEDS Mb/s)"
```

<!-- từ khóa: script mạng nic card mạng port cổng up link tốc độ speed 10gb 1gb 25gb ssh cluster kiểm tra cáp sfp rớt tốc độ đứt cáp ethtool -->
