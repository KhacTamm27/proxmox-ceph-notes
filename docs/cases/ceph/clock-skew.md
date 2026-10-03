# Clock skew trên MON (lệch giờ)

[← Mục lục](../../../README.md) · Case study Ceph

**Triệu chứng:** HEALTH_WARN "clock skew detected on mon.X", MON mất quorum chập chờn.

**Nguyên nhân hay gặp:** Đồng hồ các node lệch quá ngưỡng (mặc định 0.05 giây), NTP/chrony không chạy hoặc không tới được nguồn giờ.

## Các bước xử lý

1. Xem MON nào lệch bao nhiêu

```bash
ceph time-sync-status
```

2. Trên node lệch: kiểm tra chrony và nguồn giờ

```bash
chronyc tracking
chronyc sources -v
timedatectl
```

3. Khởi động lại chrony và ép chỉnh giờ

```bash
systemctl restart chrony
chronyc makestep
```

4. Kiểm tra lại sau vài phút

```bash
ceph time-sync-status
ceph health detail
```

## Lưu ý

Đảm bảo mọi node cùng trỏ về cùng nguồn NTP nội bộ. Nếu là VM, tắt đồng bộ giờ trùng lặp từ hypervisor.

<!-- từ khóa: ceph clock skew lệch giờ mất đồng bộ giờ ntp chrony mon -->
