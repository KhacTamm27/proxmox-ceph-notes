# Large omap objects (thường do bucket index RGW)

[← Mục lục](../../README.md)

**Triệu chứng:** HEALTH_WARN "N large omap objects".

**Nguyên nhân hay gặp:** Bucket có quá nhiều object trên ít shard của index (hoặc omap lớn ở pool khác).

## Các bước xử lý

1. Xem pool và object bị cảnh báo

```bash
ceph health detail
```

2. Tìm bucket vượt giới hạn shard

```bash
radosgw-admin bucket limit check
```

3. Reshard bucket đó (nếu dynamic resharding chưa tự xử lý)

```bash
radosgw-admin bucket reshard --bucket=<bucket> --num-shards=<n>
```

4. Cảnh báo chỉ hết sau khi deep-scrub PG chứa object cũ

```bash
ceph pg deep-scrub <pgid>
```

## Lưu ý

Chọn số shard theo số object dự kiến (khoảng 100 nghìn object mỗi shard là mức tham khảo). Nếu pool khác RGW, tìm nguyên nhân omap ở ứng dụng đang dùng pool đó.

<!-- từ khóa: ceph large omap objects rgw bucket index shard reshard cảnh báo -->
