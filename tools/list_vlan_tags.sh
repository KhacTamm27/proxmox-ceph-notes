#!/usr/bin/env bash
# Liệt kê VLAN tag/trunks đang dùng trong cấu hình VM/CT trên toàn cluster Proxmox.
# /etc/pve là pmxcfs dùng chung, nên chỉ cần chạy trên một node.

set -u

CONFIG_DIR="/etc/pve/nodes"

[[ -d "$CONFIG_DIR" ]] || {
  echo "LỖI: không tìm thấy $CONFIG_DIR (không chạy trên node Proxmox?)" >&2
  exit 1
}

shopt -s nullglob
configs=(
  "$CONFIG_DIR"/*/qemu-server/*.conf
  "$CONFIG_DIR"/*/lxc/*.conf
)

if [[ ${#configs[@]} -eq 0 ]]; then
  echo "Không tìm thấy cấu hình VM/CT trong $CONFIG_DIR."
  exit 0
fi

if matches=$(grep -hP '(tag|trunks)=\K[0-9;]+' "${configs[@]}"); then
  :
else
  status=$?
  if [[ $status -ne 1 ]]; then
    echo "LỖI: không đọc được cấu hình VLAN từ $CONFIG_DIR." >&2
    exit "$status"
  fi
fi

if [[ -z ${matches:-} ]]; then
  echo "Không tìm thấy VLAN tag/trunks trong cấu hình VM/CT."
  exit 0
fi

echo "Các VLAN ID đang được dùng trong cấu hình VM/CT trên cluster:"
printf '%s\n' "$matches" | tr ';' '\n' | sort -nu
