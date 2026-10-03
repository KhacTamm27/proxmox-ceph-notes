# Cảnh báo PG không được scrub / deep-scrub kịp thời

[← Mục lục](../../../README.md) · Case study Ceph

**Triệu chứng:** HEALTH_WARN "N pgs not deep-scrubbed in time" hoặc "not scrubbed in time".

**Nguyên nhân hay gặp:** Quên gỡ flag noscrub sau bảo trì, cửa sổ scrub quá hẹp, cluster bận hoặc số scrub đồng thời thấp.

## Các bước xử lý

1. Xem PG nào quá hạn

```bash
ceph health detail
```

2. Kiểm tra có đang bị tắt scrub bằng flag không

```bash
ceph osd dump
```

3. Xem cửa sổ scrub và cấu hình hiện tại

```bash
ceph config get osd osd_scrub_begin_hour
ceph config get osd osd_scrub_end_hour
```

4. Gỡ flag nếu có, rồi chạy deep-scrub thủ công cho PG quá hạn

```bash
ceph osd unset noscrub
ceph osd unset nodeep-scrub
ceph pg deep-scrub <pgid>
```

## Lưu ý

Nguyên nhân phổ biến nhất là flag noscrub còn sót. Đừng chạy deep-scrub hàng loạt giờ cao điểm, scrub tốn IO đĩa.

<!-- từ khóa: ceph scrub deep-scrub not scrubbed in time noscrub quên gỡ cảnh báo pg -->
