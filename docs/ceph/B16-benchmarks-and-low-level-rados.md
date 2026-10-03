# B16 · Benchmarks and low-level rados

[← Mục lục](../../README.md) · Ceph · 12 lệnh

[← B15 Authentication (cephx)](../ceph/B15-authentication-cephx.md) · [B17 Upgrade and compatibility →](../ceph/B17-upgrade-and-compatibility.md)

## Bench

```bash
# Write benchmark
rados bench -p <pool> 30 write --no-cleanup

# Sequential read benchmark
rados bench -p <pool> 30 seq

# Random read benchmark
rados bench -p <pool> 30 rand

# Remove benchmark objects
rados -p <pool> cleanup
```

## Objects

```bash
# List pools
rados lspools

# List objects (large pools: slow)
rados -p <pool> ls

# Object size and mtime
rados -p <pool> stat <object>

# Read object
rados -p <pool> get <object> <file>

# Write object
rados -p <pool> put <object> <file>

# ⚠ NGUY HIỂM: Delete object (destructive)
rados -p <pool> rm <object>
```

## Omap

```bash
# Omap keys of an object
rados -p <pool> listomapkeys <object>

# Omap key and values
rados -p <pool> listomapvals <object>
```
