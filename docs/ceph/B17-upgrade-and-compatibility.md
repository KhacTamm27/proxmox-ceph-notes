# B17 · Upgrade and compatibility

[← Mục lục](../../README.md) · Ceph · 8 lệnh

[← B16 Benchmarks and low-level rados](../ceph/B16-benchmarks-and-low-level-rados.md) · [B18 Troubleshooting shortlist →](../ceph/B18-troubleshooting-shortlist.md)

## Versions

```bash
# Mixed-version check
ceph versions
```

## Release

```bash
# Read `require_osd_release` and flags
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

# Confirm all PGs `active+clean` before next node
ceph -s
```

## Post-upgrade

```bash
# Restore normal behavior
ceph osd unset noout
```
