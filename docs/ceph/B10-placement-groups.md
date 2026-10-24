# B10 · Placement group (PG)

[← Mục lục](../../README.md) · Ceph · 16 lệnh · tên gốc: Placement groups

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← B9 Pool](../ceph/B09-pools.md) · [B11 Recovery, scrub và tinh chỉnh cấu hình →](../ceph/B11-recovery-scrub-and-config-tuning.md)

## Tóm tắt (Summary)

```bash
# [chỉ đọc] Số PG theo từng trạng thái | PG state counts
# từ khóa: pg trạng thái tổng quan
ceph pg stat

# [chỉ đọc] PG kẹt inactive (không phục vụ IO) | Stuck inactive PGs
# từ khóa: pg inactive stuck treo mất dữ liệu
ceph pg dump_stuck inactive

# [chỉ đọc] PG kẹt unclean | Stuck unclean PGs
# từ khóa: pg unclean stuck
ceph pg dump_stuck unclean

# [chỉ đọc] PG thiếu bản sao kẹt lâu | Stuck undersized PGs
# từ khóa: undersized thiếu replica
ceph pg dump_stuck undersized
```

## Liệt kê (List)

```bash
# [chỉ đọc] Liệt kê toàn bộ PG | All PGs
# từ khóa: pg danh sách
ceph pg ls

# [chỉ đọc] PG của một pool | PGs of a pool
# từ khóa: pg pool
ceph pg ls-by-pool <pool>

# [chỉ đọc] PG đang nằm trên một OSD | PGs on an OSD
# từ khóa: pg osd
ceph pg ls-by-osd osd.<id>
```

## Ánh xạ (Mapping)

```bash
# [chỉ đọc] PG này nằm trên OSD nào (up và acting) | Up and acting OSDs
# từ khóa: pg map vị trí acting
ceph pg map <pgid>
```

## Chi tiết (Detail)

```bash
# [chỉ đọc] Trạng thái chi tiết của PG, lý do bị kẹt | Full PG state
# từ khóa: pg stuck peering incomplete lý do
ceph pg <pgid> query
```

## Scrub

```bash
# Chạy scrub hoặc deep-scrub cho một PG | Scrub a PG
# từ khóa: scrub kiểm tra toàn vẹn
ceph pg scrub <pgid> / ceph pg deep-scrub <pgid>
```

## Sửa lỗi (Repair)

```bash
# Sửa PG inconsistent (xác định bản lỗi trước khi chạy) | Repair inconsistent PG
# từ khóa: inconsistent scrub error sửa pg repair
ceph pg repair <pgid>

# Ép PG peering lại | Force re-peering
# từ khóa: peering stuck
ceph pg repeer <pgid>
```

## Ưu tiên (Priority)

```bash
# Ưu tiên recovery PG này trước | Recover this PG first
# từ khóa: ưu tiên recovery
ceph pg force-recovery <pgid>

# Ưu tiên backfill PG này trước | Backfill this PG first
# từ khóa: ưu tiên backfill
ceph pg force-backfill <pgid>
```

## Upmap

```bash
# Chuyển tay PG từ OSD này sang OSD khác | Manual PG remap
# từ khóa: upmap chuyển pg cân bằng
ceph osd pg-upmap-items <pgid> <from> <to>

# Gỡ upmap thủ công của PG | Remove manual remap
# từ khóa: upmap gỡ
ceph osd rm-pg-upmap-items <pgid>
```

## Case và runbook dùng lệnh trong nhóm này

- [PG degraded / undersized, recovery chậm](../cases/ceph/pg-degraded-recovery.md)
- [Thêm OSD hoặc node mới làm chậm production](../cases/ceph/add-osd-throttle.md)
- [PG down, peering kẹt hoặc unfound objects (mất nhiều OSD)](../cases/ceph/pg-down-incomplete.md)
- [PG inconsistent / scrub errors](../cases/ceph/pg-inconsistent.md)
- [Large omap objects (thường do bucket index RGW)](../cases/ceph/large-omap.md)
- [Cảnh báo PG không được scrub / deep-scrub kịp thời](../cases/ceph/deep-scrub-late.md)
