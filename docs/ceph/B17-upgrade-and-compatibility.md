# B17 · Upgrade and compatibility

[← Mục lục](../../README.md) · Ceph · 8 lệnh

[← B16 Benchmarks and low-level rados](../ceph/B16-benchmarks-and-low-level-rados.md) · [B18 Troubleshooting shortlist →](../ceph/B18-troubleshooting-shortlist.md)

## Versions

```bash
# Phiên bản các daemon, kiểm tra lệch version khi nâng cấp | Mixed-version check
# từ khóa: version nâng cấp upgrade mixed
ceph versions
```

## Release

```bash
# OSD map: flag, ratio, thông tin pool | Read `require_osd_release` and flags
# từ khóa: flags noout full ratio pool
ceph osd dump

# Finalize OSD release after upgrade
ceph osd require-osd-release <release>
```

## Clients

```bash
# Minimum client version (needed for upmap)
ceph osd set-require-min-compat-client <release>

# Connected client feature levels
ceph features
```

## Pre-upgrade

```bash
# Avoid rebalance during rolling restart
ceph osd set noout

# Tổng quan sức khỏe cluster Ceph, lệnh đầu tiên cần chạy | Confirm all PGs `active+clean` before next node
# từ khóa: status health tổng quan kiểm tra nhanh
ceph -s
```

## Post-upgrade

```bash
# Restore normal behavior
ceph osd unset noout
```
