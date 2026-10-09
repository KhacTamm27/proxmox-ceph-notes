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
