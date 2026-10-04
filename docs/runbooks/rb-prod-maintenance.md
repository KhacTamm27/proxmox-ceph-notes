# Bảo trì production: tắt HA và đặt cờ bảo trì Ceph trước khi tắt node

[← Mục lục](../../README.md) · Runbook

**Mục tiêu:** Tắt hoặc reboot node trong môi trường production mà không kích hoạt fencing/HA di chuyển VM đồng loạt, và không để Ceph backfill/recovery không cần thiết.

**Điều kiện trước khi làm:** Kiểm tra sức khỏe Ceph trước (ceph -s). Tránh thao tác khi đang có cảnh báo Warn hoặc Err nếu chưa được cấp trên cho phép.

## Các bước

1. Kiểm tra trước khi làm

```bash
ceph -s
ha-manager status
```

2. Tắt HA. Lý do: nếu không, khi một node dừng, fencing đánh dấu node dead rồi các VM được dừng và khởi động lại trên host khác; số VM lớn đồng loạt bật lên làm tràn RAM và gây sập dây chuyền (domino). Dừng pve-ha-lrm ở TẤT CẢ các host trước

```bash
systemctl stop pve-ha-lrm
```

3. Sau khi lrm đã dừng ở mọi host mới dừng pve-ha-crm. Không làm đồng loạt cả hai

```bash
systemctl stop pve-ha-crm
```

4. Maintain Ceph. Lý do: tắt node hoặc dừng OSD không báo trước thì cluster coi là mất đột ngột, báo HEALTH_WARN/ERR và backfill sang OSD khác, gây I/O thừa ảnh hưởng workload. Trên GUI: Ceph, OSD, Manage Global Flags, chọn 6 cờ rồi Apply. Dòng lệnh tương đương

```bash
ceph osd set noout
ceph osd set nobackfill
ceph osd set norecover
ceph osd set norebalance
ceph osd set noscrub
ceph osd set nodeep-scrub
```

5. Xác nhận 6 cờ đã bật

```bash
ceph osd dump | grep flags
ceph -s
```

6. Thực hiện bảo trì (tắt, sửa, reboot node), chờ node và OSD lên lại

```bash
ceph osd stat
pvecm status
```

7. Hoàn tác: bỏ 6 cờ trước

```bash
ceph osd unset noout
ceph osd unset nobackfill
ceph osd unset norecover
ceph osd unset norebalance
ceph osd unset noscrub
ceph osd unset nodeep-scrub
```

8. Bật lại HA (thứ tự start không có trong ghi chú gốc, thường lrm rồi crm), kiểm tra

```bash
systemctl start pve-ha-lrm
systemctl start pve-ha-crm
ha-manager status
```

## Lưu ý

Quên bỏ cờ sau bảo trì là lỗi hay gặp, xem case cờ bảo trì còn sót. Ngoài ra cần đủ RAM dự phòng (N+1) để các VM của một node chết vẫn chạy được trên node còn lại.

<!-- từ khóa: runbook bảo trì maintenance production tắt ha pve-ha-lrm pve-ha-crm ceph flags noout nobackfill norecover norebalance noscrub nodeep-scrub manage global flags -->
