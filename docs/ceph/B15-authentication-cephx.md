# B15 · Authentication (cephx)

[← Mục lục](../../README.md) · Ceph · 6 lệnh

[← B14 CephFS](../ceph/B14-cephfs.md) · [B16 Benchmarks and low-level rados →](../ceph/B16-benchmarks-and-low-level-rados.md)

## List

```bash
# Toàn bộ key và quyền | All keys and caps
# từ khóa: auth key quyền cephx
ceph auth ls
```

## Show

```bash
# Một key và quyền của nó | One key and caps
# từ khóa: auth key client
ceph auth get client.<name>

# In ra secret của key | Print secret only
# từ khóa: secret key
ceph auth print-key client.<name>
```

## Create

```bash
# Tạo key cho client | Create client key
# từ khóa: tạo key client cephx
ceph auth get-or-create client.<name> mon 'allow r' osd 'allow rwx pool=<pool>'
```

## Change

```bash
# Đổi quyền của key | Change caps
# từ khóa: đổi quyền caps cephx
ceph auth caps client.<name> mon 'allow r' osd 'allow rw pool=<pool>'
```

## Delete

```bash
# ⚠ NGUY HIỂM: Xóa key (nguy hiểm) | Remove key (destructive)
# từ khóa: xóa key
ceph auth del client.<name>
```
