# Cờ bảo trì Ceph còn sót sau bảo trì (noout, noscrub, norecover...)

[← Mục lục](../../../README.md) · Case study Ceph

**Triệu chứng:** HEALTH_WARN "noout,nobackfill,norecover,norebalance,noscrub,nodeep-scrub flag(s) set", PG không recover, cảnh báo scrub quá hạn.

**Nguyên nhân hay gặp:** Quên bỏ các cờ đã đặt trước khi bảo trì hoặc nâng cấp. Khi còn noout, OSD chết thật cũng không được out để recover, còn norecover và nobackfill làm dữ liệu giữ trạng thái degraded.

## Các bước xử lý

1. Xem cờ nào đang bật (cũng thấy ở GUI: Ceph, OSD, Manage Global Flags)

```bash
ceph health detail
ceph osd dump | grep flags
```

2. Bỏ từng cờ khi bảo trì đã xong và cluster đã ổn

```bash
ceph osd unset noout
ceph osd unset nobackfill
ceph osd unset norecover
ceph osd unset norebalance
ceph osd unset noscrub
ceph osd unset nodeep-scrub
```

3. Theo dõi recovery và scrub chạy lại

```bash
ceph -s
ceph -w
```

## Lưu ý

Nên chỉ bỏ cờ khi đã chắc mọi OSD up/in. Bỏ cờ xong recovery và backfill sẽ chạy dồn nên có thể ảnh hưởng IO, tham khảo case thêm OSD làm chậm production để giảm tải. Ghi checklist đặt cờ và bỏ cờ vào quy trình bảo trì.

<!-- từ khóa: ceph flags còn sót quên gỡ noout nobackfill norecover norebalance noscrub nodeep-scrub health warn flag(s) set unset bảo trì -->
