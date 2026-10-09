# Slow ops / blocked requests

[← Mục lục](../../../README.md) · Case study Ceph

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

5. Nếu nghi DB/metadata RocksDB phình lớn hoặc BlueFS spillover, kiểm tra mức dùng trên OSD chậm

```bash
ceph daemon osd.<osd-id> perf dump bluefs
```

6. Xác nhận cluster vẫn khỏe trước khi thử compaction

```bash
ceph -s
```

7. Nếu DB metadata trên chính OSD chậm phình lớn (ví dụ khoảng 100 GB), compact riêng OSD đó; trường hợp đã quan sát: osd.72

```bash
ceph tell osd.<osd-id> compact
```

8. So sánh lại latency và trạng thái cluster sau thao tác

```bash
ceph osd perf
ceph -w
```

## Lưu ý

ceph tell osd.<id> compact ép RocksDB compact các bảng dữ liệu; lệnh này không xóa object hay metadata còn cần thiết, không xóa dữ liệu người dùng. Khi DB metadata phình lớn là nguyên nhân gây chậm, compact có thể thu gọn DB metadata và giảm latency OSD — đã quan sát thực tế trên osd.72. So sánh dung lượng DB metadata và ceph osd perf trước/sau để xác nhận hiệu quả. Kết quả không áp dụng cho mọi nguyên nhân latency; compaction tự nó tốn I/O và có thể làm latency tăng tạm thời, nên chỉ chạy trên OSD nghi vấn khi cluster khỏe, từng OSD một. ~100 GB là dấu hiệu trong trường hợp này, không phải ngưỡng áp dụng chung. Nhớ ceph osd unset noscrub sau khi xử lý xong.

<!-- từ khóa: ceph slow ops blocked requests chậm treo latency io osd db rocksdb metadata bluefs spillover compact -->
