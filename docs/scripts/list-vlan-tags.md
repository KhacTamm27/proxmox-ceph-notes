# Liệt kê VLAN tag/trunks đang dùng trên toàn cluster

[← Mục lục](../../README.md) · Script tiện ích

**Mục đích:** Tổng hợp các VLAN ID có tag hoặc trunks trong cấu hình VM/CT trên mọi node Proxmox, giúp kiểm tra VLAN nào đang được sử dụng trước khi cấu hình switch hoặc bridge.

## Cách dùng

```bash
./list_vlan_tags.sh    # Liệt kê VLAN ID duy nhất từ cấu hình VM và container trên cluster
```

File gốc: [`tools/list_vlan_tags.sh`](../../tools/list_vlan_tags.sh)

## Lưu ý

Chạy trên một node Proxmox đang hoạt động; không cần SSH vì /etc/pve/nodes là pmxcfs dùng chung toàn cluster. Script chỉ đọc cấu hình VM/CT, tìm các trường tag= và trunks=, rồi tách và sắp xếp VLAN ID duy nhất; không thay đổi cấu hình hay trạng thái mạng. Cần Bash và GNU grep hỗ trợ PCRE (-P).

## Mã nguồn

```bash
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
```

<!-- từ khóa: script proxmox pve vlan tag trunk trunks vlan id vm ct qemu lxc cluster network mạng kiểm tra cấu hình -->
