# Slow ops / blocked requests

[← Mục lục](../../README.md)

**Triệu chứng:** HEALTH_WARN "N slow ops", VM đơ hoặc IO chậm, "requests are blocked".

**Nguyên nhân hay gặp:** Một OSD hoặc đĩa chậm, mạng nghẽn, recovery/scrub chiếm tải giờ cao điểm.

## Các bước xử lý

1. Xem OSD nào bị ảnh hưởng

```bash
ceph health detail
ceph osd perf
```

2. Trên host của OSD chậm: xem thao tác đang kẹt

```bash
ceph daemon osd.<id> dump_ops_in_flight
```

3. Kiểm tra đĩa và mạng của host đó

```bash
iostat -x 1
ethtool -S <if>
```

4. Nếu recovery hoặc scrub đang chiếm tải: giảm tải và ưu tiên client

```bash
ceph config set osd osd_max_backfills 1
ceph config set osd osd_mclock_profile high_client_ops
ceph osd set noscrub
```

## Lưu ý

Nhớ ceph osd unset noscrub sau khi xử lý xong. Một OSD có latency cao bất thường thường là đĩa sắp hỏng.

<!-- từ khóa: ceph slow ops blocked requests chậm treo latency io -->
