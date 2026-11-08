# Kiểm tra NIC / bond / corosync link từng node (check-10Gb.sh)

[← Mục lục](../../README.md) · Script tiện ích

**Mục đích:** Kiểm tra nhanh tình trạng mạng của toàn cluster Proxmox, mỗi node một dòng trong bảng; dùng trước và sau khi bảo trì mạng, thay switch/cáp/card, hoặc khi nghi ngờ LACP và link corosync có vấn đề. Script chỉ đọc thông tin, không đổi cấu hình. Cổng DATA lấy trực tiếp từ Linux bond hoặc OVS bond, không đoán theo tốc độ hay model card, nên chạy được trên phần cứng hỗn hợp và không cần ethtool.

## Cách dùng

```bash
./check-10Gb.sh    # Kiểm tra tất cả node trong /etc/pve/.members
./check-10Gb.sh node1 node2    # Chỉ kiểm tra các node được chỉ định
MIN_SPEED=1000 ./check-10Gb.sh    # Đặt ngưỡng mỗi bond slave cần đạt là 1000 Mb/s (mặc định 10000)
```

File gốc: [`tools/check-10Gb.sh`](../../tools/check-10Gb.sh)

## Lưu ý

Các cột: HOST và IP lấy từ /etc/pve/.members; BOND là tên bond và mode; DATA PORTS liệt kê mọi slave cùng link/tốc độ. PAIR là trạng thái bond data: OK (mọi slave UP và >= MIN_SPEED), SLOW (mọi slave UP nhưng có slave chậm), PARTIAL (một số slave DOWN), ALL-DOWN (mọi slave DOWN), NO-BOND hoặc BOND-EMPTY. COR là trạng thái corosync: OK (mọi link có port UP >=1G, có ít nhất 2 link và ít nhất một link ngoài bond data), DOWN, SLOW (<1G), NO-DEDICATED hoặc SINGLE. COROSYNC LINKS map từng ringN_addr trong /etc/pve/corosync.conf tới cổng vật lý thật qua bridge, bond, VLAN hoặc OVS, kèm trạng thái/tốc độ. OTHER PORTS liệt kê cổng vật lý còn lại, IP riêng, bridge master hoặc [unused]. Chạy bằng root trên một node PVE; cần SSH key không mật khẩu giữa các node, python3 và ovs-appctl nếu node dùng OVS bond. Danh sách node và link corosync đọc từ /etc/pve/.members và /etc/pve/corosync.conf, vì vậy /etc/pve phải đang mount; không chạy được sau khi stop pve-cluster. Node offline/SSH lỗi hiện UNREACHABLE. Exit code 0 nếu mọi node OK, 1 nếu có node cần chú ý (PAIR PARTIAL/SLOW/ALL-DOWN/NO-BOND/UNREACHABLE hoặc COR DOWN/SLOW/NO-DEDICATED/SINGLE), phù hợp dùng trong cron/giám sát. Bỏ qua cổng SR-IOV VF. Tốc độ đọc từ /sys/class/net/<nic>/speed; card ảo hoặc link down có thể không báo tốc độ. Màu chỉ hiện trên terminal. SSH dùng StrictHostKeyChecking=no.

## Mã nguồn

```bash
#!/usr/bin/env bash
#
# check-10Gb.sh  (v2 - bond-based, works on mixed hardware)
# Per-node NIC check for a Proxmox cluster (Linux bond / Linux bridge / OVS).
# Output: one table row per node.
#
# DATA ports are taken from the BOND itself (Linux bond slaves, or OVS bond
# members), NOT guessed from NIC speed/model. ethtool is not required.
#
#   BOND           : bond name + mode, e.g. bond0(lacp), bond0(ovs:balance-tcp/lacp-negotiated)
#   DATA PORTS     : every slave of the bond(s) with link state + speed
#   PAIR           : OK        all slaves UP and >= MIN_SPEED
#                    SLOW      all UP but at least one < MIN_SPEED
#                    PARTIAL   some slaves DOWN
#                    ALL-DOWN  every slave DOWN
#                    NO-BOND   no bond found on the node
#                    BOND-EMPTY bond exists but no member ports could be read
#   COR            : OK            every corosync link has a port UP, >=1G, >=2 links,
#                                  and at least one link on a port outside the data bond
#                    DOWN          a corosync link has no port UP
#                    SLOW          a corosync link is UP but < 1G (e.g. 100M)
#                    NO-DEDICATED  all corosync links ride on the data bond only
#                    SINGLE        only one corosync link (no redundancy)
#   COROSYNC LINKS : every ringN_addr in /etc/pve/corosync.conf, resolved to the
#                    real physical port(s) with UP/DOWN + speed
#   OTHER PORTS    : remaining physical ports
#                    nicX:UP(10G)=1.2.3.4  standalone port with IP
#                    nicX:UP(1G)>vmbr0     port enslaved to a bridge
#                    nicX:DOWN[unused]     no IP, no master (spare)
#
# Usage:
#   ./check-10Gb.sh                 # all nodes in /etc/pve/.members
#   ./check-10Gb.sh node1 node2     # only the given nodes
#   MIN_SPEED=1000 ./check-10Gb.sh  # Mb/s each bond slave must reach (default 10000)
#
# Requirements: root on a PVE node, passwordless SSH between nodes (PVE default),
#               python3 (and ovs-appctl on nodes that use OVS bonds).

MEMBERS="/etc/pve/.members"
COROSYNC_CONF="/etc/pve/corosync.conf"
MIN_SPEED="${MIN_SPEED:-10000}"
SSH_OPTS="-o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=no -o LogLevel=ERROR"

[ -r "$MEMBERS" ] || { echo "ERROR: cannot read $MEMBERS (not a PVE node?)" >&2; exit 2; }
command -v python3 >/dev/null || { echo "ERROR: python3 not found" >&2; exit 2; }

# ---------------------------------------------------------------------------
# Remote probe (runs on each node). Arg: <links "0=ip,1=ip,...">
# Output lines:
#   BOND|<bond>|<mode>
#   SLV|<bond>|<iface>|<UP/DOWN>|<speed Mb/s or ->
#   NIC|<iface>|<UP/DOWN>|<speed Mb/s or ->|<master or ->|<ipv4 or ->
#   COR|<link>|<ip>|<phys iface>|<UP/DOWN/NOTFOUND/NONE>|<speed Mb/s or ->
# ---------------------------------------------------------------------------
read -r -d '' REMOTE <<'EOF'
LINKS="${1:-}"

link_state() { [ "$(cat /sys/class/net/$1/carrier 2>/dev/null)" = "1" ] && echo UP || echo DOWN; }
link_speed() {
  local s; s=$(cat /sys/class/net/$1/speed 2>/dev/null)
  case "$s" in ''|-1|*[!0-9]*) echo "-";; *) echo "$s";; esac
}
short_mode() {
  case "$1" in
    *802.3ad*)       echo lacp ;;
    *active-backup*) echo active-backup ;;
    *xor*)           echo xor ;;
    *round-robin*)   echo rr ;;
    *adaptive*)      echo alb ;;
    *transmit*)      echo tlb ;;
    *broadcast*)     echo broadcast ;;
    *)               echo "${1:-?}" ;;
  esac
}

# Physical ports of the OVS bridge that owns port/bridge $1
ovs_phys() {
  command -v ovs-vsctl >/dev/null 2>&1 || return 1
  local br m
  br=$(ovs-vsctl port-to-br "$1" 2>/dev/null)
  if [ -z "$br" ]; then ovs-vsctl br-exists "$1" 2>/dev/null && br="$1"; fi
  [ -n "$br" ] || return 1
  for m in $(ovs-vsctl list-ifaces "$br" 2>/dev/null); do
    [ -e "/sys/class/net/$m/device" ] && echo "$m"
  done
}

# Resolve bridge / bond / VLAN / OVS port down to physical NIC(s)
resolve() {
  local d="$1" m
  if [ -d "/sys/class/net/$d/brif" ]; then
    for m in $(ls "/sys/class/net/$d/brif"); do resolve "$m"; done
  elif [ -r "/sys/class/net/$d/bonding/slaves" ]; then
    for m in $(cat "/sys/class/net/$d/bonding/slaves"); do resolve "$m"; done
  elif [ -r "/proc/net/vlan/$d" ]; then
    resolve "$(awk '/^Device:/{print $2}' "/proc/net/vlan/$d")"
  elif [[ "$d" == *.* ]]; then
    resolve "${d%%.*}"
  elif [ -e "/sys/class/net/$d/device" ]; then
    echo "$d"
  else
    ovs_phys "$d"
  fi
}

# --- Linux bonds ---
for b in $(ls /proc/net/bonding 2>/dev/null); do
  mode=$(short_mode "$(awk -F': ' '/^Bonding Mode/{print $2; exit}' /proc/net/bonding/$b)")
  echo "BOND|$b|$mode"
  for s in $(cat /sys/class/net/$b/bonding/slaves 2>/dev/null); do
    echo "SLV|$b|$s|$(link_state "$s")|$(link_speed "$s")"
  done
done

# --- OVS bonds ---
if command -v ovs-appctl >/dev/null 2>&1; then
  for b in $(ovs-appctl bond/list 2>/dev/null | awk 'NR>1{print $1}'); do
    info=$(ovs-appctl bond/show "$b" 2>/dev/null)
    mode=$(echo "$info" | awk '/^bond_mode:/{print $2; exit}')
    lacp=$(echo "$info" | awk '/^lacp_status:/{print $2; exit}')
    echo "BOND|$b|ovs:${mode:-?}${lacp:+/lacp-$lacp}"
    # OVS >= 3.x prints "member NIC: enabled", older versions print "slave NIC: enabled"
    members=$(echo "$info" | awk '/^(slave|member) /{sub(":","",$2); print $2}')
    if [ -z "$members" ] && command -v ovs-vsctl >/dev/null 2>&1; then
      # version-independent fallback: port -> interface UUIDs -> names
      for u in $(ovs-vsctl get port "$b" interfaces 2>/dev/null | tr -d '[],'); do
        members="$members $(ovs-vsctl get interface "$u" name 2>/dev/null | tr -d '"')"
      done
    fi
    for s in $members; do
      echo "SLV|$b|$s|$(link_state "$s")|$(link_speed "$s")"
    done
  done
fi

# --- All physical ports (skip SR-IOV VFs) ---
for p in /sys/class/net/*; do
  i="${p##*/}"
  [ -e "$p/device" ] || continue
  [ -e "$p/device/physfn" ] && continue
  m=$(readlink "$p/master" 2>/dev/null); master=${m##*/}; master=${master:--}
  ip4=$(ip -o -4 addr show dev "$i" 2>/dev/null | awk '{print $4; exit}'); ip4=${ip4%%/*}; ip4=${ip4:--}
  echo "NIC|$i|$(link_state "$i")|$(link_speed "$i")|$master|$ip4"
done

# --- Corosync links -> physical ports ---
if [ -z "$LINKS" ]; then
  echo "COR|-|-|-|NONE|-"
else
  IFS=',' read -ra arr <<<"$LINKS"
  for kv in "${arr[@]}"; do
    n="${kv%%=*}"; a="${kv#*=}"
    [ -n "$a" ] || continue
    dev=$(ip -o -4 addr show | awk -v ip="$a" '{split($4,x,"/"); if (x[1]==ip) {print $2; exit}}')
    if [ -z "$dev" ]; then echo "COR|$n|$a|-|NOTFOUND|-"; continue; fi
    found=0
    for phy in $(resolve "$dev" | sort -u); do
      found=1
      echo "COR|$n|$a|$phy|$(link_state "$phy")|$(link_speed "$phy")"
    done
    [ "$found" -eq 0 ] && echo "COR|$n|$a|$dev|NOTFOUND|-"
  done
fi
EOF

# ---------------------------------------------------------------------------
# Node list: name|ip|online|links  (links = "0=ip,1=ip,...")
# ---------------------------------------------------------------------------
mapfile -t NODES < <(python3 - "$MEMBERS" "$COROSYNC_CONF" <<'PY'
import json, re, socket, sys
members, conf = sys.argv[1], sys.argv[2]
nodes = json.load(open(members)).get("nodelist", {})
rings = {}
try:
    txt = open(conf).read()
    for blk in re.findall(r"node\s*\{(.*?)\}", txt, re.S):
        n = re.search(r"name:\s*(\S+)", blk)
        if not n:
            continue
        lst = []
        for num, addr in re.findall(r"ring(\d+)_addr:\s*(\S+)", blk):
            try:
                addr = socket.gethostbyname(addr)
            except Exception:
                pass
            lst.append("%s=%s" % (num, addr))
        rings[n.group(1)] = ",".join(lst)
except Exception:
    pass
for name, v in sorted(nodes.items(), key=lambda x: x[1].get("id", 0)):
    print("%s|%s|%s|%s" % (name, v.get("ip", ""), v.get("online", 0), rings.get(name, "")))
PY
)

[ "${#NODES[@]}" -gt 0 ] || { echo "ERROR: no nodes found in $MEMBERS" >&2; exit 2; }

FILTER=" $* "

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
if [ -t 1 ]; then R=$'\033[31m'; G=$'\033[32m'; Y=$'\033[33m'; N=$'\033[0m'; else R=; G=; Y=; N=; fi
colorize() {
  sed -e "s/\bUP\b/${G}UP${N}/g" -e "s/\bOK\b/${G}OK${N}/g" \
      -e "s/\bDOWN\b/${R}DOWN${N}/g" -e "s/ALL-DOWN/${R}ALL-DOWN${N}/g" \
      -e "s/PARTIAL/${Y}PARTIAL${N}/g" -e "s/\bSLOW\b/${Y}SLOW${N}/g" \
      -e "s/NO-DEDICATED/${Y}NO-DEDICATED${N}/g" -e "s/\bSINGLE\b/${Y}SINGLE${N}/g" \
      -e "s/NO-BOND/${R}NO-BOND${N}/g" -e "s/BOND-EMPTY/${R}BOND-EMPTY${N}/g" \
      -e "s/NOTFOUND/${R}NOTFOUND${N}/g" -e "s/UNREACHABLE/${R}UNREACHABLE${N}/g"
}

fmt() {  # <state> <speed Mb/s or ->
  if [ "$1" = "UP" ] && [ "$2" != "-" ]; then
    if [ "$2" -ge 1000 ]; then echo "UP($(($2 / 1000))G)"; else echo "UP(${2}M)"; fi
  else
    echo "$1"
  fi
}

# ---------------------------------------------------------------------------
# Collect one row per node
# ---------------------------------------------------------------------------
BAD=0
ROWS=()
for entry in "${NODES[@]}"; do
  IFS='|' read -r name ip online links <<<"$entry"
  if [ "$#" -gt 0 ] && [[ "$FILTER" != *" $name "* ]]; then continue; fi

  if [ "$name" = "$(hostname -s)" ]; then
    out=$(bash -s -- "$links" <<<"$REMOTE" 2>/dev/null)
  else
    out=$(ssh $SSH_OPTS "root@$ip" "bash -s -- '$links'" <<<"$REMOTE" 2>/dev/null)
  fi

  if [ -z "$out" ]; then
    ROWS+=("$name|$ip|-|-|UNREACHABLE|-|-|-")
    BAD=$((BAD + 1))
    continue
  fi

  nics=(); bonds=""; data=""; dtotal=0; dup=0; dslow=0
  unset DATASET CORIF CORIP CORUP CORUSED CORPH CORBEST
  declare -A DATASET CORIF CORIP CORUP CORUSED CORPH CORBEST

  while IFS='|' read -r tag a b c d e; do
    case "$tag" in
      BOND) bonds+="${bonds:+ }$a($b)" ;;
      SLV)  DATASET[$b]=1
            data+="${data:+ }$b:$(fmt "$c" "$d")"
            dtotal=$((dtotal + 1))
            if [ "$c" = "UP" ]; then
              dup=$((dup + 1))
              if [[ "$d" =~ ^[0-9]+$ ]] && [ "$d" -lt "$MIN_SPEED" ]; then dslow=$((dslow + 1)); fi
            fi ;;
      NIC)  nics+=("$a|$b|$c|$d|$e") ;;
      COR)  [ "$d" = "NONE" ] && continue
            CORIP[$a]="$b"
            if [ "$d" = "NOTFOUND" ]; then
              lbl="$c"; [ "$lbl" = "-" ] && lbl="$b"   # show the ring address that is not on any local NIC
              CORIF[$a]+="${CORIF[$a]:+,}$lbl:NOTFOUND"
            else
              CORIF[$a]+="${CORIF[$a]:+,}$c:$(fmt "$d" "$e")"
              CORUSED[$c]=1
              CORPH[$a]+=" $c"
              if [ "$d" = "UP" ]; then
                CORUP[$a]=1
                if [[ "$e" =~ ^[0-9]+$ ]] && [ "$e" -gt "${CORBEST[$a]:-0}" ]; then CORBEST[$a]="$e"; fi
              fi
            fi ;;
    esac
  done <<<"$out"

  # --- other physical ports (not in the data bond, not used by corosync) ---
  other=""
  for n in "${nics[@]}"; do
    IFS='|' read -r ifc st spd master ip4 <<<"$n"
    [ -n "${DATASET[$ifc]:-}" ] && continue
    [ -n "${CORUSED[$ifc]:-}" ] && continue
    tok="$ifc:$(fmt "$st" "$spd")"
    if   [ "$ip4" != "-" ];    then tok+="=$ip4"
    elif [ "$master" != "-" ]; then tok+=">$master"
    else                            tok+="[unused]"
    fi
    other+="${other:+ }$tok"
  done

  # --- data bond status ---
  if   [ "$dtotal" -eq 0 ] && [ -n "$bonds" ]; then pair="BOND-EMPTY"
  elif [ "$dtotal" -eq 0 ];      then pair="NO-BOND"
  elif [ "$dup" -eq 0 ];         then pair="ALL-DOWN"
  elif [ "$dup" -lt "$dtotal" ]; then pair="PARTIAL"
  elif [ "$dslow" -gt 0 ];       then pair="SLOW"
  else                                pair="OK"
  fi

  # --- corosync status ---
  nlinks=${#CORIP[@]}; cor=""; cdown=0; cslow=0; cdedicated=0
  for n in $(printf '%s\n' "${!CORIP[@]}" | sort -n); do
    cor+="${cor:+ }L$n:${CORIF[$n]}"
    [ -z "${CORUP[$n]:-}" ] && cdown=1
    if [ -n "${CORBEST[$n]:-}" ] && [ "${CORBEST[$n]}" -lt 1000 ]; then cslow=1; fi
    for ph in ${CORPH[$n]:-}; do
      [ -z "${DATASET[$ph]:-}" ] && cdedicated=1
    done
  done
  if   [ "$nlinks" -eq 0 ];    then corstat="N/A"
  elif [ "$cdown" -eq 1 ];     then corstat="DOWN"
  elif [ "$cslow" -eq 1 ];     then corstat="SLOW"
  elif [ "$cdedicated" -eq 0 ]; then corstat="NO-DEDICATED"
  elif [ "$nlinks" -eq 1 ];    then corstat="SINGLE"
  else                              corstat="OK"
  fi

  if [ "$pair" != "OK" ] || { [ "$corstat" != "OK" ] && [ "$corstat" != "N/A" ]; }; then
    BAD=$((BAD + 1))
  fi

  ROWS+=("$name|$ip|${bonds:--}|${data:--}|$pair|$corstat|${cor:--}|${other:--}")
done

[ "${#ROWS[@]}" -gt 0 ] || { echo "No matching nodes." >&2; exit 2; }

# ---------------------------------------------------------------------------
# Print table (auto column widths)
# ---------------------------------------------------------------------------
HDR=("HOST" "IP" "BOND" "DATA PORTS" "PAIR" "COR" "COROSYNC LINKS" "OTHER PORTS")
W=()
for h in "${HDR[@]}"; do W+=("${#h}"); done
for row in "${ROWS[@]}"; do
  IFS='|' read -ra c <<<"$row"
  for i in "${!c[@]}"; do
    [ "${#c[$i]}" -gt "${W[$i]}" ] && W[$i]="${#c[$i]}"
  done
done

print_line() {  # args: cells...
  local i line="" k=0
  for i in "$@"; do
    line+="$(printf '%-*s' "${W[$k]}" "$i")  "
    k=$((k + 1))
  done
  echo "${line%  }"
}

print_line "${HDR[@]}"
dashes=()
for w in "${W[@]}"; do dashes+=("$(printf '%*s' "$w" '' | tr ' ' '-')"); done
print_line "${dashes[@]}"

for row in "${ROWS[@]}"; do
  IFS='|' read -ra c <<<"$row"
  print_line "${c[@]}" | colorize
done

echo
if [ "$BAD" -eq 0 ]; then
  echo "Result: all checked nodes OK (data bond up at >= ${MIN_SPEED} Mb/s, corosync links healthy)."
else
  echo "Result: $BAD node(s) need attention (PAIR: PARTIAL/SLOW/ALL-DOWN/NO-BOND/UNREACHABLE; COR: DOWN/SLOW/NO-DEDICATED/SINGLE)."
  exit 1
fi
```

<!-- từ khóa: script check-10Gb check-10gb NIC bond LACP OVS corosync link speed 10G ethtool kiểm tra mạng bảo trì switch cáp network port physical link -->
