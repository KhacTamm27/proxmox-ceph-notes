# B16 · Benchmarks and low-level rados

[← Mục lục](../../README.md) · Ceph · 12 lệnh

[← B15 Authentication (cephx)](../ceph/B15-authentication-cephx.md) · [B17 Upgrade and compatibility →](../ceph/B17-upgrade-and-compatibility.md)

## Bench

```bash
# Benchmark ghi | Write benchmark
# từ khóa: benchmark ghi hiệu năng
rados bench -p <pool> 30 write --no-cleanup

# Benchmark đọc tuần tự | Sequential read benchmark
# từ khóa: benchmark đọc
rados bench -p <pool> 30 seq

# Benchmark đọc ngẫu nhiên | Random read benchmark
# từ khóa: benchmark đọc ngẫu nhiên
rados bench -p <pool> 30 rand

# Xóa object benchmark | Remove benchmark objects
# từ khóa: dọn benchmark
rados -p <pool> cleanup
```

## Objects

```bash
# Liệt kê pool | List pools
# từ khóa: pool danh sách
rados lspools

# Liệt kê object (pool lớn sẽ chậm) | List objects (large pools: slow)
# từ khóa: object danh sách
rados -p <pool> ls

# Kích thước và thời gian của object | Object size and mtime
# từ khóa: object stat
rados -p <pool> stat <object>

# Đọc object ra file | Read object
# từ khóa: đọc object
rados -p <pool> get <object> <file>

# Ghi file vào object | Write object
# từ khóa: ghi object
rados -p <pool> put <object> <file>

# ⚠ NGUY HIỂM: Xóa object (nguy hiểm) | Delete object (destructive)
# từ khóa: xóa object
rados -p <pool> rm <object>
```

## Omap

```bash
# Đếm key omap của object nghi lớn | Omap keys of an object
# từ khóa: large omap object
rados -p <pool> listomapkeys <object>

# Key và giá trị omap | Omap key and values
# từ khóa: omap large omap
rados -p <pool> listomapvals <object>
```
