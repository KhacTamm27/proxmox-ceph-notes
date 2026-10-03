# Cảnh báo too many / too few PGs, chỉnh pg_num

[← Mục lục](../../../README.md) · Case study Ceph

**Triệu chứng:** HEALTH_WARN "too many PGs per OSD" hoặc "pool has too few/many pgs".

**Nguyên nhân hay gặp:** Số PG của pool không hợp với số OSD hiện có (thêm hoặc bớt OSD, tạo nhiều pool).

## Các bước xử lý

1. Xem autoscaler đề xuất gì cho từng pool

```bash
ceph osd pool autoscale-status
```

2. Xem số PG trên mỗi OSD

```bash
ceph osd df
ceph health detail
```

3. Để autoscaler tự điều chỉnh (khuyến nghị)

```bash
ceph osd pool set <pool> pg_autoscale_mode on
```

## Lưu ý

Đổi pg_num gây di chuyển dữ liệu, làm vào giờ thấp tải và theo dõi ceph -s. Khoảng 100 PG mỗi OSD là mức tham khảo.

<!-- từ khóa: ceph pg number too many pgs per osd too few autoscale pg_num pool -->
