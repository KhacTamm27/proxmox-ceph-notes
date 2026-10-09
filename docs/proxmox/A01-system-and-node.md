# A1 · System and node

[← Mục lục](../../README.md) · Proxmox host · 21 lệnh

[A2 Cluster and corosync →](../proxmox/A02-cluster-and-corosync.md)

## Version

```bash
# Xem phiên bản PVE và các gói liên quan | PVE and package versions
# từ khóa: version phiên bản kernel gói nâng cấp kiểm tra
pveversion -v

# Xem hostname và hệ điều hành | Hostname, OS
# từ khóa: hostname tên máy os debian
hostnamectl

# Xem kernel đang chạy | Running kernel
# từ khóa: kernel phiên bản nhân boot
uname -r
```

## Load

```bash
# Thời gian máy chạy và mức tải | Uptime and load
# từ khóa: uptime load tải reboot lần cuối
uptime
```

## Time

```bash
# Múi giờ và trạng thái đồng bộ giờ | Time zone and sync state
# từ khóa: giờ ntp lệch giờ timezone clock
timedatectl

# Độ lệch NTP trên máy hiện tại | NTP offset
# từ khóa: ntp chrony lệch giờ clock skew
chronyc tracking

# Xem các nguồn NTP đang dùng | NTP sources
# từ khóa: ntp chrony nguồn giờ lệch giờ
chronyc sources -v
```

## Services

```bash
# Liệt kê service đang bị lỗi | Failed units
# từ khóa: service lỗi failed sau reboot không chạy
systemctl --failed

# Trạng thái các service lõi của PVE | Core PVE services
# từ khóa: service pve gui treo pveproxy pvedaemon pvestatd
systemctl status pve-cluster pvedaemon pveproxy pvestatd pve-firewall pvescheduler
```

## Node

```bash
# Xem cấu hình của node | Node config
# từ khóa: node config cấu hình
pvenode config get

# Bật toàn bộ VM/CT trên node | Start all guests on node
# từ khóa: khởi động tất cả sau bảo trì start all
pvenode startall

# Tắt toàn bộ VM/CT trên node | Stop all guests on node
# từ khóa: tắt tất cả trước bảo trì stop all
pvenode stopall

# Di chuyển toàn bộ VM/CT sang node khác | Migrate all guests away
# từ khóa: bảo trì node migrate hết reboot
pvenode migrateall <target-node>
```

## Certificates

```bash
# Xem thông tin chứng chỉ của node | Certificate details
# từ khóa: chứng chỉ ssl cert hết hạn
pvenode cert info

# Tạo lại chứng chỉ cho cluster | Regenerate cluster certificates
# từ khóa: chứng chỉ lỗi ssh known_hosts node mới join cert
pvecm updatecerts --force
```

## Upgrade

```bash
# Cập nhật danh sách gói từ repo | Refresh package lists
# từ khóa: apt repo cập nhật nâng cấp
apt update

# Nâng cấp toàn bộ gói (kể cả thêm/xóa gói phụ thuộc) | Upgrade packages
# từ khóa: nâng cấp upgrade cập nhật hệ thống
apt full-upgrade

# Công cụ kiểm tra trước khi nâng cấp PVE 8 lên 9 | Pre-upgrade checker (PVE 8 to 9)
# từ khóa: nâng cấp upgrade 8 9 kiểm tra trước
pve8to9 --full
```

## Kernel

```bash
# Xem cấu hình boot (ESP, kernel) | Boot setup status
# từ khóa: boot uefi esp lỗi boot grub systemd-boot
proxmox-boot-tool status

# Liệt kê các kernel đã cài | Installed kernels
# từ khóa: kernel danh sách phiên bản
proxmox-boot-tool kernel list

# Ghim kernel mặc định khi boot | Pin default kernel
# từ khóa: kernel pin ghim lỗi sau nâng cấp quay về kernel cũ
proxmox-boot-tool kernel pin <version>
```
