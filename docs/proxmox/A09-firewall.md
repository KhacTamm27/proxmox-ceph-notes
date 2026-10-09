# A9 · Firewall

[← Mục lục](../../README.md) · Proxmox host · 5 lệnh

[← A8 Network](../proxmox/A08-network.md) · [A10 Disks and filesystems →](../proxmox/A10-disks-and-filesystems.md)

## Status

```bash
# Trạng thái firewall PVE | Firewall state
# từ khóa: firewall tường lửa trạng thái chặn
pve-firewall status

# Các mạng nội bộ được nhận diện | Detected local networks
# từ khóa: localnet mạng nội bộ
pve-firewall localnet
```

## Rules

```bash
# Xem các rule sau khi biên dịch | Show generated rules
# từ khóa: rule firewall biên dịch
pve-firewall compile

# Xem rule firewall cấp cluster | Cluster-level rules
# từ khóa: firewall cluster rule
cat /etc/pve/firewall/cluster.fw
```

## Control

```bash
# Khởi động lại firewall | Restart firewall
# từ khóa: restart firewall
pve-firewall restart
```
