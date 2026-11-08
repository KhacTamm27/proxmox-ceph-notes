# Menu Stop / Start / Status HA và Cluster (pve-ha-lrm, pve-ha-crm, pve-cluster, corosync) trên toàn cluster

[← Mục lục](../../README.md) · Script tiện ích

**Mục đích:** Tắt hoặc bật đồng loạt HA và dịch vụ cluster trên mọi node đúng thứ tự khi bảo trì production, thay vì gõ tay từng node. Stop HA theo thứ tự LRM rồi CRM; start CRM, chờ bầu master, rồi LRM. Stop cluster theo thứ tự pve-cluster rồi corosync; start corosync rồi pve-cluster. Tương ứng các bước tắt HA và dừng cluster trong runbook bảo trì production.

## Cách dùng

```bash
./menu-ha.sh    # Mở menu: 1 Stop HA, 2 Start HA, 3 Xem trạng thái HA, 4 Stop cluster, 5 Start cluster, 6 Xem trạng thái pve-cluster / corosync, 7 Chuẩn bị SSH dự phòng, 0 Thoát
```

File gốc: [`tools/menu-ha.sh`](../../tools/menu-ha.sh)

## Lưu ý

Chạy từ MỘT node trong cluster, cần SSH key root giữa các node. Danh sách lấy TẤT CẢ node và ring0_addr từ corosync.conf, kể cả node offline: ưu tiên /etc/pve/corosync.conf, rồi /etc/corosync/corosync.conf; có cache dự phòng /root/.menu-ha-nodes.cache. Node offline vẫn được thử SSH và báo [FAIL] hoặc unreachable; kiểm tra lại khi node online. Phải Stop HA (mục 1) trước khi Stop cluster (mục 4): nếu pve-ha-lrm còn active khi dừng cluster/corosync, node có thể bị watchdog reset. Script cảnh báo và hỏi xác nhận nếu phát hiện LRM còn chạy. Trên Proxmox, /root/.ssh/authorized_keys là symlink tới /etc/pve/priv/authorized_keys; khi stop pve-cluster thì /etc/pve biến mất. Vì vậy mục 4 tự chạy mục 7 để chép public key vào /root/.ssh/authorized_keys2 (file local) trên mọi node và kiểm tra sshd có đọc file này. Nếu chuẩn bị thất bại trên node nào, có thể không SSH start lại được node đó; cần console/IPMI hoặc SSH bằng mật khẩu. Mục 1 và 2 cảnh báo nếu cluster không có quorum; menu hỏi xác nhận trước thao tác. Trong lúc HA tắt, VM HA không tự phục hồi nếu node chết, nên chỉ tắt trong khung bảo trì; xong chọn 2 để bật lại rồi xem ha-manager status. Khi start cluster (mục 5), đợi khoảng 8 giây cho /etc/pve mount và lên quorum, kiểm tra mục 6 và pvecm status trước khi Start HA. Các lệnh SSH dùng StrictHostKeyChecking=no và UserKnownHostsFile=/dev/null. Quy trình gợi ý: 1 Stop HA → 4 Stop cluster → bảo trì → 5 Start cluster → 2 Start HA → 3 kiểm tra.

## Mã nguồn

```bash
#!/bin/bash
# menu-ha.sh - Stop/start/status pve-ha-lrm, pve-ha-crm, pve-cluster, corosync trên toàn bộ node Proxmox
# Chạy từ MỘT node trong cluster. Lấy TẤT CẢ node + IP từ corosync.conf (kể cả node offline).
# Có cache dự phòng và đọc được cả khi /etc/pve đã bị unmount (sau khi stop pve-cluster).

SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=5 -o BatchMode=yes"
CACHE_FILE="/root/.menu-ha-nodes.cache"

declare -A NODE_IP

# --- Lấy danh sách node ---
# Lấy TẤT CẢ node (cả node đang offline) từ file corosync.conf.
# Ưu tiên /etc/pve/corosync.conf; nếu /etc/pve không còn (pve-cluster đã stop) thì dùng
# bản copy local /etc/corosync/corosync.conf (file này luôn có trên mỗi node).
COROSYNC_CONF="/etc/pve/corosync.conf"
[ -s "$COROSYNC_CONF" ] || COROSYNC_CONF="/etc/corosync/corosync.conf"

while read -r name ip; do
  [ -n "$name" ] && NODE_IP[$name]=$ip
done < <(awk '
  /^[[:space:]]*node[[:space:]]*\{/ { inn=1; name=""; ip="" }
  inn && /^[[:space:]]*name:/       { name=$2 }
  inn && /^[[:space:]]*ring0_addr:/ { ip=$2 }
  inn && /^[[:space:]]*\}/          { if (name != "" && ip != "") print name, ip; inn=0 }
' "$COROSYNC_CONF" 2>/dev/null)

if [ ${#NODE_IP[@]} -gt 0 ]; then
  # Lưu cache để dự phòng
  for n in "${!NODE_IP[@]}"; do echo "$n ${NODE_IP[$n]}"; done > "$CACHE_FILE"
elif [ -s "$CACHE_FILE" ]; then
  # Không đọc được corosync.conf -> dùng cache
  while read -r name ip; do
    [ -n "$name" ] && NODE_IP[$name]=$ip
  done < "$CACHE_FILE"
  echo "LƯU Ý: không đọc được corosync.conf, dùng danh sách node đã cache ($CACHE_FILE)."
  sleep 2
fi

NODES=$(printf '%s\n' "${!NODE_IP[@]}" | sort -V)

if [ -z "$NODES" ]; then
  echo "Không lấy được danh sách node từ corosync.conf (và chưa có cache)."
  exit 1
fi

run_all() {   # run_all <service> <action>
  local svc=$1 action=$2
  for n in $NODES; do
    (
      out=$(ssh $SSH_OPTS root@"${NODE_IP[$n]}" "systemctl $action $svc" 2>&1)
      if [ $? -eq 0 ]; then
        echo "  [OK]   $n: $action $svc"
      else
        echo "  [FAIL] $n (${NODE_IP[$n]}): $action $svc -> ${out%%$'\n'*}"
      fi
    ) &
  done
  wait
}

check_quorum() {
  if ! pvecm status 2>/dev/null | grep -q "Quorate:.*Yes"; then
    echo "CẢNH BÁO: Cluster KHÔNG có quorum!"
    read -rp "Vẫn tiếp tục? (y/N): " a
    [[ "$a" =~ ^[Yy]$ ]] || return 1
  fi
  return 0
}

# Cảnh báo nếu LRM còn đang chạy (stop cluster/corosync khi LRM active có thể làm node bị watchdog reboot)
check_lrm_stopped() {
  local active=""
  for n in $NODES; do
    s=$(ssh $SSH_OPTS root@"${NODE_IP[$n]}" "systemctl is-active pve-ha-lrm" 2>/dev/null)
    [ "$s" = "active" ] && active+="$n "
  done
  if [ -n "$active" ]; then
    echo
    echo "CẢNH BÁO: pve-ha-lrm vẫn đang chạy trên: $active"
    echo "Stop cluster/corosync khi LRM còn active có thể khiến node bị watchdog reset (reboot)!"
    echo "Nên chạy mục 1 (Stop HA) trước."
    read -rp "Vẫn tiếp tục? (y/N): " a
    [[ "$a" =~ ^[Yy]$ ]] || return 1
  fi
  return 0
}

show_status() {
  echo
  printf "%-20s %-12s %-12s\n" "NODE" "CRM" "LRM"
  printf "%-20s %-12s %-12s\n" "----" "---" "---"
  for n in $NODES; do
    crm=$(ssh $SSH_OPTS root@"${NODE_IP[$n]}" "systemctl is-active pve-ha-crm" 2>/dev/null)
    lrm=$(ssh $SSH_OPTS root@"${NODE_IP[$n]}" "systemctl is-active pve-ha-lrm" 2>/dev/null)
    printf "%-20s %-12s %-12s\n" "$n" "${crm:-unreachable}" "${lrm:-unreachable}"
  done
  echo
}

show_cluster_status() {
  echo
  printf "%-20s %-14s %-12s\n" "NODE" "PVE-CLUSTER" "COROSYNC"
  printf "%-20s %-14s %-12s\n" "----" "-----------" "--------"
  for n in $NODES; do
    pc=$(ssh $SSH_OPTS root@"${NODE_IP[$n]}" "systemctl is-active pve-cluster" 2>/dev/null)
    co=$(ssh $SSH_OPTS root@"${NODE_IP[$n]}" "systemctl is-active corosync" 2>/dev/null)
    printf "%-20s %-14s %-12s\n" "$n" "${pc:-unreachable}" "${co:-unreachable}"
  done
  echo
}

stop_ha() {
  check_quorum || return
  echo
  echo "=== Bước 1/2: Stop pve-ha-lrm trên tất cả node ==="
  run_all pve-ha-lrm stop
  echo "=== Bước 2/2: Stop pve-ha-crm trên tất cả node ==="
  run_all pve-ha-crm stop
  show_status
}

start_ha() {
  check_quorum || return
  echo
  echo "=== Bước 1/2: Start pve-ha-crm trên tất cả node ==="
  run_all pve-ha-crm start
  echo "Chờ CRM bầu master..."
  sleep 5
  echo "=== Bước 2/2: Start pve-ha-lrm trên tất cả node ==="
  run_all pve-ha-lrm start
  show_status
  echo "=== HA status ==="
  ha-manager status
}

# Trên Proxmox, /root/.ssh/authorized_keys là symlink sang /etc/pve/priv/authorized_keys.
# Khi stop pve-cluster thì /etc/pve biến mất -> SSH bằng key bị từ chối.
# Hàm này chép public key của node hiện tại vào /root/.ssh/authorized_keys2 (file thật, nằm local)
# trên tất cả node để vẫn SSH được sau khi stop pve-cluster.
prepare_ssh() {
  local keys results
  keys=$(cat /root/.ssh/id_*.pub 2>/dev/null)
  if [ -z "$keys" ]; then
    echo "Không tìm thấy public key /root/.ssh/id_*.pub trên node này."
    return 1
  fi
  echo
  echo "=== Chuẩn bị SSH dự phòng (authorized_keys2) trên tất cả node ==="
  results=$(
    for n in $NODES; do
      (
        if ! printf '%s\n' "$keys" | ssh $SSH_OPTS root@"${NODE_IP[$n]}" 'f=/root/.ssh/authorized_keys2; mkdir -p /root/.ssh; cat >> "$f"; sort -u -o "$f" "$f"; chmod 600 "$f"' 2>/dev/null; then
          echo "  [FAIL] $n: không ghi được authorized_keys2"; exit 1
        fi
        if ! ssh -n $SSH_OPTS root@"${NODE_IP[$n]}" "sshd -T 2>/dev/null | grep -qi '^authorizedkeysfile.*authorized_keys2'"; then
          echo "  [FAIL] $n: sshd chưa cho đọc authorized_keys2"; exit 1
        fi
        echo "  [OK]   $n"
      ) &
    done
    wait
  )
  echo "$results" | sort -V
  if echo "$results" | grep -q FAIL; then
    echo
    echo "CẢNH BÁO: có node chưa chuẩn bị được. Nếu stop cluster, anh sẽ KHÔNG SSH start lại được các node đó"
    echo "(phải vào console/IPMI hoặc SSH bằng mật khẩu để start tay)."
    read -rp "Vẫn tiếp tục? (y/N): " a
    [[ "$a" =~ ^[Yy]$ ]] || return 1
  fi
  return 0
}

stop_cluster() {
  check_lrm_stopped || return
  prepare_ssh || { echo "Đã hủy, chưa stop gì cả."; return; }
  echo
  echo "=== Bước 1/2: Stop pve-cluster trên tất cả node ==="
  run_all pve-cluster stop
  echo "=== Bước 2/2: Stop corosync trên tất cả node ==="
  run_all corosync stop
  show_cluster_status
}

start_cluster() {
  echo
  echo "=== Bước 1/2: Start corosync trên tất cả node ==="
  run_all corosync start
  echo "Chờ corosync khởi động..."
  sleep 3
  echo "=== Bước 2/2: Start pve-cluster trên tất cả node ==="
  run_all pve-cluster start
  echo "Chờ pve-cluster mount /etc/pve và lên quorum..."
  sleep 5
  show_cluster_status
  echo "=== Cluster status ==="
  pvecm status 2>&1 | head -n 20
}

confirm() {
  read -rp "$1 (y/N): " a
  [[ "$a" =~ ^[Yy]$ ]]
}

while true; do
  clear
  echo "=========================================="
  echo "   PROXMOX HA / CLUSTER MANAGER"
  echo "=========================================="
  echo "Node trong cluster (${#NODE_IP[@]}): $(echo $NODES | tr '\n' ' ')"
  echo
  echo "  --- HA ---"
  echo "  1) Stop HA   (LRM -> CRM) trên tất cả node"
  echo "  2) Start HA  (CRM -> LRM) trên tất cả node"
  echo "  3) Xem trạng thái HA"
  echo
  echo "  --- CLUSTER ---"
  echo "  4) Stop cluster  (pve-cluster -> corosync) trên tất cả node"
  echo "  5) Start cluster (corosync -> pve-cluster) trên tất cả node"
  echo "  6) Xem trạng thái pve-cluster / corosync"
  echo "  7) Chuẩn bị SSH dự phòng (chạy trước khi stop cluster; mục 4 tự chạy bước này)"
  echo
  echo "  0) Thoát"
  echo
  read -rp "Chọn [0-7]: " choice

  case "$choice" in
    1) confirm "Xác nhận STOP HA trên toàn cluster?"  && stop_ha ;;
    2) confirm "Xác nhận START HA trên toàn cluster?" && start_ha ;;
    3) show_status; ha-manager status 2>/dev/null ;;
    4) confirm "Xác nhận STOP pve-cluster + corosync trên toàn cluster?" && stop_cluster ;;
    5) confirm "Xác nhận START corosync + pve-cluster trên toàn cluster?" && start_cluster ;;
    6) show_cluster_status ;;
    7) prepare_ssh ;;
    0) echo "Bye."; exit 0 ;;
    *) echo "Lựa chọn không hợp lệ." ;;
  esac

  echo
  read -rp "Nhấn Enter để quay lại menu..." _
done
```

<!-- từ khóa: script ha stop start status lrm crm pve-ha-lrm pve-ha-crm pve-cluster corosync cluster node ring0_addr quorum authorized_keys2 ssh bảo trì maintenance tắt ha bật ha menu fence domino -->
