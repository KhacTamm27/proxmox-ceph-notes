# OSD không lên sau reboot

[← Mục lục](../../../README.md) · Case study Ceph

**Triệu chứng:** Sau reboot một số OSD vẫn down, systemctl báo failed hoặc start-limit-hit.

**Nguyên nhân hay gặp:** LVM chưa activate, đĩa đổi tên thiết bị hoặc không còn nhận, service chạm giới hạn số lần restart.

## Các bước xử lý

1. Xem OSD nào down và trạng thái service

```bash
ceph osd tree down
systemctl status ceph-osd@<osd-id>
```

2. Đọc log tìm lỗi mở đĩa hoặc bluestore

```bash
journalctl -u ceph-osd@<osd-id> --since "30 min ago"
```

3. Kiểm tra đĩa và LVM của OSD có còn không

```bash
lsblk
ceph-volume lvm list
```

4. Activate lại và start OSD

```bash
ceph-volume lvm activate --all
systemctl reset-failed ceph-osd@<osd-id>
systemctl start ceph-osd@<osd-id>
```

## Lưu ý

Nếu lsblk không còn thấy đĩa thì là lỗi phần cứng, chuyển sang case thay đĩa OSD. Đừng dùng ceph-volume lvm create trên đĩa đang chứa OSD cũ vì sẽ xóa dữ liệu.

<!-- từ khóa: ceph osd không start sau reboot ceph-volume lvm activate không thấy đĩa failed -->
