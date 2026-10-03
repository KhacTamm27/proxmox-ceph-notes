# B14 · CephFS

[← Mục lục](../../README.md) · Ceph · 8 lệnh

[← B13 RGW and S3 (radosgw-admin)](../ceph/B13-rgw-and-s3-radosgw-admin.md) · [B15 Authentication (cephx) →](../ceph/B15-authentication-cephx.md)

## Status

```bash
# List filesystems
ceph fs ls

# Ranks, clients, usage
ceph fs status

# MDS states
ceph mds stat

# Filesystem map
ceph fs get <fs>
```

## Create

```bash
# Create filesystem
ceph fs new <fs> <metadata-pool> <data-pool>
```

## Subvolume

```bash
# List subvolumes
ceph fs subvolume ls <fs>
```

## Failover

```bash
# Fail an MDS
ceph mds fail <name-or-rank>
```

## Delete

```bash
# ⚠ NGUY HIỂM: Delete filesystem (destructive)
ceph fs rm <fs> --yes-i-really-mean-it
```
