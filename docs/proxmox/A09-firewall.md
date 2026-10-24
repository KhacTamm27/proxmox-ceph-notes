# A9 · Tường lửa

[← Mục lục](../../README.md) · Proxmox host · 5 lệnh · tên gốc: Firewall

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← A8 Mạng](../proxmox/A08-network.md) · [A10 Ổ đĩa và filesystem →](../proxmox/A10-disks-and-filesystems.md)

## Trạng thái (Status)

```bash
# [chỉ đọc] Trạng thái firewall PVE | Firewall state
# từ khóa: firewall tường lửa trạng thái chặn
pve-firewall status

# [chỉ đọc] Các mạng nội bộ được nhận diện | Detected local networks
# từ khóa: localnet mạng nội bộ
pve-firewall localnet
```

## Rule (Rules)

```bash
# Xem các rule sau khi biên dịch | Show generated rules
# từ khóa: rule firewall biên dịch
pve-firewall compile

# [chỉ đọc] Xem rule firewall cấp cluster | Cluster-level rules
# từ khóa: firewall cluster rule
cat /etc/pve/firewall/cluster.fw
```

## Điều khiển (Control)

```bash
# Khởi động lại firewall | Restart firewall
# từ khóa: restart firewall
pve-firewall restart
```
