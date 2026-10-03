# PG degraded / undersized, recovery chậm

[← Mục lục](../../README.md)

**Triệu chứng:** HEALTH_WARN "Degraded data redundancy", "N pgs undersized/degraded", "objects misplaced", recovery chạy lâu.

**Nguyên nhân hay gặp:** Mất OSD hoặc node, vừa thêm OSD mới, hoặc recovery bị giới hạn quá thấp.

## Các bước xử lý

1. Xem mức độ và OSD nào đang thiếu

```bash
ceph health detail
ceph pg stat
ceph osd tree down
```

2. Tìm PG kẹt lâu và lý do

```bash
ceph pg dump_stuck undersized
ceph pg <pgid> query
```

3. Nếu muốn recovery nhanh hơn (chấp nhận ảnh hưởng client): ưu tiên PG quan trọng hoặc đổi profile

```bash
ceph pg force-recovery <pgid>
ceph config set osd osd_mclock_profile high_recovery_ops
```

4. Xong thì trả cấu hình về mặc định

```bash
ceph config rm osd osd_mclock_profile
```

## Lưu ý

Trong lúc degraded, cluster có ít bản sao hơn bình thường, đừng bảo trì thêm node nào. Giờ cao điểm nên giữ profile ưu tiên client.

<!-- từ khóa: ceph pg degraded undersized misplaced recovery chậm backfill thiếu replica -->
