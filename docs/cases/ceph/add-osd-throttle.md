# Thêm OSD hoặc node mới làm chậm production

[← Mục lục](../../../README.md) · Case study Ceph

**Triệu chứng:** Sau khi thêm OSD hoặc node, VM chậm, nhiều PG backfilling, objects misplaced.

**Nguyên nhân hay gặp:** Rebalance và backfill chiếm IO đĩa và mạng cùng lúc với tải client.

## Các bước xử lý

1. Theo dõi tiến độ rebalance

```bash
ceph -s
ceph pg stat
```

2. Giảm tải backfill và ưu tiên client

```bash
ceph config set osd osd_max_backfills 1
ceph config set osd osd_mclock_profile high_client_ops
```

3. Nếu cần tạm dừng hẳn trong giờ cao điểm, nhớ gỡ sau

```bash
ceph osd set nobackfill
ceph osd unset nobackfill
```

## Lưu ý

Nên thêm OSD từng chút một, ngoài giờ cao điểm. Khi muốn rebalance nhanh lại thì dùng profile high_recovery_ops hoặc xóa cấu hình đã đặt.

<!-- từ khóa: ceph thêm osd node mới rebalance backfill chậm io client throttle mở rộng -->
