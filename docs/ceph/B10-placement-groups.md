# B10 · Placement groups

[← Mục lục](../../README.md) · Ceph · 16 lệnh

[← B9 Pools](../ceph/B09-pools.md) · [B11 Recovery, scrub and config tuning →](../ceph/B11-recovery-scrub-and-config-tuning.md)

## Summary

```bash
# PG state counts
ceph pg stat

# Stuck inactive PGs
ceph pg dump_stuck inactive

# Stuck unclean PGs
ceph pg dump_stuck unclean

# Stuck undersized PGs
ceph pg dump_stuck undersized
```

## List

```bash
# All PGs
ceph pg ls

# PGs of a pool
ceph pg ls-by-pool <pool>

# PGs on an OSD
ceph pg ls-by-osd osd.<id>
```

## Mapping

```bash
# Up and acting OSDs
ceph pg map <pgid>
```

## Detail

```bash
# Full PG state
ceph pg <pgid> query
```

## Scrub

```bash
# Scrub a PG
ceph pg scrub <pgid> / ceph pg deep-scrub <pgid>
```

## Repair

```bash
# Repair inconsistent PG
ceph pg repair <pgid>

# Force re-peering
ceph pg repeer <pgid>
```

## Priority

```bash
# Recover this PG first
ceph pg force-recovery <pgid>

# Backfill this PG first
ceph pg force-backfill <pgid>
```

## Upmap

```bash
# Manual PG remap
ceph osd pg-upmap-items <pgid> <from> <to>

# Remove manual remap
ceph osd rm-pg-upmap-items <pgid>
```
