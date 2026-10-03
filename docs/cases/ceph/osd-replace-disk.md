# Thay đĩa OSD hỏng

[← Mục lục](../../../README.md) · Case study Ceph

**Triệu chứng:** OSD down kéo dài, SMART báo lỗi hoặc dmesg có I/O error, cần thay đĩa vật lý.

**Nguyên nhân hay gặp:** Đĩa hết tuổi thọ hoặc bad sector.

## Các bước xử lý

1. Xác định OSD hỏng và xác nhận đĩa lỗi

```bash
ceph osd tree down
ceph osd metadata <osd-id>
smartctl -a /dev/<dev>
```

2. Đánh dấu out để dữ liệu được dựng lại trên các OSD khác, đợi các PG về active+clean

```bash
ceph osd out <osd-id>
ceph -w
```

3. Dừng OSD và kiểm tra an toàn trước khi xóa

```bash
systemctl stop ceph-osd@<osd-id>
ceph osd safe-to-destroy <osd-id>
```

4. Xóa OSD khỏi cluster (Proxmox)

```bash
pveceph osd destroy <osd-id> --cleanup
```

5. Thay đĩa vật lý rồi tạo OSD mới, theo dõi backfill

```bash
pveceph osd create /dev/<dev>
ceph -s
```

## Lưu ý

Chỉ xóa OSD khi safe-to-destroy trả về an toàn. Thay từng đĩa một, đợi cluster về HEALTH_OK rồi mới thay đĩa tiếp theo.

<!-- từ khóa: ceph osd thay đĩa hỏng disk replace smart pveceph rebuild -->
