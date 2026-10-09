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

# Chốt phiên bản OSD sau nâng cấp | Finalize OSD release after upgrade
# từ khóa: nâng cấp upgrade require-osd-release cảnh báo
ceph osd require-osd-release <release>
```

## Clients

```bash
# Phiên bản client tối thiểu (cần cho upmap) | Minimum client version (needed for upmap)
# từ khóa: compat client upmap balancer
ceph osd set-require-min-compat-client <release>

# Mức tính năng của các client đang kết nối | Connected client feature levels
# từ khóa: client feature phiên bản cũ
ceph features
```

## Pre-upgrade

```bash
# Tránh rebalance khi restart lần lượt | Avoid rebalance during rolling restart
# từ khóa: noout bảo trì nâng cấp
ceph osd set noout

# Tổng quan sức khỏe cluster Ceph, lệnh đầu tiên cần chạy | Confirm all PGs `active+clean` before next node
# từ khóa: status health tổng quan kiểm tra nhanh
ceph -s
```

## Post-upgrade

```bash
# Trả về hoạt động bình thường | Restore normal behavior
# từ khóa: gỡ noout xong bảo trì
ceph osd unset noout
```
