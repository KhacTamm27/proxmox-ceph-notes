# B6 · Vòng đời OSD và thiết bị

[← Mục lục](../../README.md) · Ceph · 15 lệnh · tên gốc: OSD lifecycle and devices

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← B5 Cờ OSD và bảo trì](../ceph/B05-osd-flags-and-maintenance.md) · [B7 Daemon OSD và hiệu năng (admin socket) →](../ceph/B07-osd-daemon-and-performance-admin-socket.md)

## Kiểm kê (Inventory)

```bash
# [chỉ đọc] Thiết bị có thể dùng làm OSD (chạy trên host OSD) | Devices usable for OSDs (on OSD host)
# từ khóa: đĩa trống inventory thêm osd
ceph-volume inventory

# [chỉ đọc] Ánh xạ OSD tới thiết bị (chạy trên host OSD) | OSD to device mapping (on OSD host)
# từ khóa: osd đĩa lvm ánh xạ không lên
ceph-volume lvm list
```

## Tạo mới (Create)

```bash
# Tạo OSD (chạy trên host OSD) | Create OSD (on OSD host)
# từ khóa: tạo osd đĩa mới
ceph-volume lvm create --data /dev/<dev>

# Kích hoạt lại các OSD sau reboot | Activate OSDs after reboot
# từ khóa: osd không lên sau reboot activate
ceph-volume lvm activate --all
```

## Thay thế (Replace)

```bash
# ⚠ NGUY HIỂM: Hủy OSD nhưng giữ ID (nguy hiểm) | Destroy OSD, keep ID (destructive)
# từ khóa: thay đĩa giữ id osd destroy
ceph osd destroy <osd-id> --yes-i-really-mean-it
```

## Gỡ bỏ (Remove)

```bash
# ⚠ NGUY HIỂM: Xóa hẳn OSD khỏi cluster (nguy hiểm) | Remove OSD from cluster (destructive)
# từ khóa: xóa osd purge thay đĩa
ceph osd purge <osd-id> --yes-i-really-mean-it
```

## Xóa sạch đĩa (Wipe)

```bash
# ⚠ NGUY HIỂM: Xóa sạch thiết bị (nguy hiểm) | Wipe device (destructive)
# từ khóa: xóa đĩa zap tái sử dụng
ceph-volume lvm zap /dev/<dev> --destroy
```

## Dịch vụ (Service)

```bash
# [chỉ đọc] Trạng thái daemon OSD | OSD daemon state
# từ khóa: osd service trạng thái failed
systemctl status ceph-osd@<osd-id>

# Khởi động lại OSD | Restart OSD
# từ khóa: restart osd
systemctl restart ceph-osd@<osd-id>

# [chỉ đọc] Theo dõi log OSD | OSD log
# từ khóa: log osd crash
journalctl -u ceph-osd@<osd-id> -f
```

## BlueStore

```bash
# [chỉ đọc] Đọc nhãn OSD trên thiết bị | Read OSD label
# từ khóa: bluestore label osd đĩa nhận diện
ceph-bluestore-tool show-label --dev /dev/<dev>

# Kiểm tra store của OSD (OSD phải dừng) | Check store (OSD stopped)
# từ khóa: bluestore fsck kiểm tra hỏng
ceph-bluestore-tool fsck --path /var/lib/ceph/osd/ceph-<id>
```

## Bảo trì (Maintenance)

```bash
# Nén RocksDB của OSD | Compact RocksDB
# từ khóa: compact rocksdb spillover chậm
ceph tell osd.<id> compact
```

## Device class (Class)

```bash
# Đặt device class cho OSD | Set device class
# từ khóa: device class ssd nvme hdd
ceph osd crush set-device-class nvme osd.<id>

# Gỡ device class của OSD | Remove device class
# từ khóa: device class gỡ
ceph osd crush rm-device-class osd.<id>
```

## Case và runbook dùng lệnh trong nhóm này

- [OSD không lên sau reboot](../cases/ceph/osd-wont-start.md)
- [OSD down hoặc up/down liên tục (flapping)](../cases/ceph/osd-down-flapping.md)
- [Slow ops / blocked requests (Ceph chậm, IO bị chặn)](../cases/ceph/slow-ops.md)
- [BLUEFS_SPILLOVER: metadata RocksDB tràn sang đĩa chậm](../cases/ceph/bluefs-spillover.md)
