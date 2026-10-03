# B15 · Authentication (cephx)

[← Mục lục](../../README.md) · Ceph · 6 lệnh

[← B14 CephFS](../ceph/B14-cephfs.md) · [B16 Benchmarks and low-level rados →](../ceph/B16-benchmarks-and-low-level-rados.md)

## List

```bash
# All keys and caps
ceph auth ls
```

## Show

```bash
# One key and caps
ceph auth get client.<name>

# Print secret only
ceph auth print-key client.<name>
```

## Create

```bash
# Create client key
ceph auth get-or-create client.<name> mon 'allow r' osd 'allow rwx pool=<pool>'
```

## Change

```bash
# Change caps
ceph auth caps client.<name> mon 'allow r' osd 'allow rw pool=<pool>'
```

## Delete

```bash
# ⚠ NGUY HIỂM: Remove key (destructive)
ceph auth del client.<name>
```
