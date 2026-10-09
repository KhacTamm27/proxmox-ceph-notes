#!/bin/bash
# ha-menu.sh - Stop/start/status pve-ha-lrm & pve-ha-crm trên toàn bộ node Proxmox
# Chạy từ MỘT node trong cluster. Lấy node + IP từ /etc/pve/.members (chỉ node online).

SSH_OPTS="-o StrictHostKeyChecking=no -o ConnectTimeout=5 -o BatchMode=yes"

declare -A NODE_IP
while read -r name ip; do
  NODE_IP[$name]=$ip
done < <(sed -nE 's/^[[:space:]]*"([^"]+)": \{ "id": [0-9]+, "online": 1, "ip": "([^"]+)".*/\1 \2/p' /etc/pve/.members)

NODES=$(printf '%s\n' "${!NODE_IP[@]}" | sort -V)

if [ -z "$NODES" ]; then
  echo "Không lấy được danh sách node từ /etc/pve/.members."
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

confirm() {
  read -rp "$1 (y/N): " a
  [[ "$a" =~ ^[Yy]$ ]]
}

while true; do
  clear
  echo "=========================================="
  echo "   PROXMOX HA MANAGER"
  echo "=========================================="
  echo "Node trong cluster (${#NODE_IP[@]}): $(echo $NODES | tr '\n' ' ')"
  echo
  echo "  1) Stop HA   (LRM -> CRM) trên tất cả node"
  echo "  2) Start HA  (CRM -> LRM) trên tất cả node"
  echo "  3) Xem trạng thái HA"
  echo "  0) Thoát"
  echo
  read -rp "Chọn [0-3]: " choice

  case "$choice" in
    1) confirm "Xác nhận STOP HA trên toàn cluster?"  && stop_ha ;;
    2) confirm "Xác nhận START HA trên toàn cluster?" && start_ha ;;
    3) show_status; ha-manager status 2>/dev/null ;;
    0) echo "Bye."; exit 0 ;;
    *) echo "Lựa chọn không hợp lệ." ;;
  esac

  echo
  read -rp "Nhấn Enter để quay lại menu..." _
done
