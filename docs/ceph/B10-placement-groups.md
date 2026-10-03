# B10 · Placement groups

[← Mục lục](../../README.md) · Ceph · 16 lệnh

[← B9 Pools](../ceph/B09-pools.md) · [B11 Recovery, scrub and config tuning →](../ceph/B11-recovery-scrub-and-config-tuning.md)

## Summary

```bash
# Số PG theo từng trạng thái | PG state counts
# từ khóa: pg trạng thái tổng quan
ceph pg stat

# PG kẹt inactive (không phục vụ IO) | Stuck inactive PGs
# từ khóa: pg inactive stuck treo mất dữ liệu
ceph pg dump_stuck inactive

# PG kẹt unclean | Stuck unclean PGs
# từ khóa: pg unclean stuck
ceph pg dump_stuck unclean

# PG thiếu bản sao kẹt lâu | Stuck undersized PGs
# từ khóa: undersized thiếu replica
ceph pg dump_stuck undersized
```

## List

```bash
# Liệt kê toàn bộ PG | All PGs
# từ khóa: pg danh sách
ceph pg ls

# PG của một pool | PGs of a pool
# từ khóa: pg pool
ceph pg ls-by-pool <pool>

# PG đang nằm trên một OSD | PGs on an OSD
# từ khóa: pg osd
ceph pg ls-by-osd osd.<id>
```

## Mapping

```bash
# PG này nằm trên OSD nào (up và acting) | Up and acting OSDs
# từ khóa: pg map vị trí acting
ceph pg map <pgid>
```

## Detail

```bash
# Trạng thái chi tiết của PG, lý do bị kẹt | Full PG state
# từ khóa: pg stuck peering incomplete lý do
ceph pg <pgid> query
```

## Scrub

```bash
# Chạy scrub hoặc deep-scrub cho một PG | Scrub a PG
# từ khóa: scrub kiểm tra toàn vẹn
ceph pg scrub <pgid> / ceph pg deep-scrub <pgid>
```

## Repair

```bash
# Sửa PG inconsistent (xác định bản lỗi trước khi chạy) | Repair inconsistent PG
# từ khóa: inconsistent scrub error sửa pg repair
ceph pg repair <pgid>

# Ép PG peering lại | Force re-peering
# từ khóa: peering stuck
ceph pg repeer <pgid>
```

## Priority

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
