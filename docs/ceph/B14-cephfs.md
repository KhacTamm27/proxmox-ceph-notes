# B14 · CephFS

[← Mục lục](../../README.md) · Ceph · 8 lệnh

[← B13 RGW and S3 (radosgw-admin)](../ceph/B13-rgw-and-s3-radosgw-admin.md) · [B15 Authentication (cephx) →](../ceph/B15-authentication-cephx.md)

## Status

```bash
# Liệt kê CephFS | List filesystems
# từ khóa: cephfs danh sách
ceph fs ls

# Rank, client và dung lượng của CephFS | Ranks, clients, usage
# từ khóa: cephfs mds rank client
ceph fs status

# Trạng thái MDS | MDS states
# từ khóa: mds trạng thái
ceph mds stat

# Bản đồ filesystem | Filesystem map
# từ khóa: cephfs map
ceph fs get <fs>
```

## Create

```bash
# Tạo filesystem | Create filesystem
# từ khóa: tạo cephfs
ceph fs new <fs> <metadata-pool> <data-pool>
```

## Subvolume

```bash
# Liệt kê subvolume | List subvolumes
# từ khóa: subvolume
ceph fs subvolume ls <fs>
```

## Failover

```bash
# Ép MDS failover | Fail an MDS
# từ khóa: mds failover treo
ceph mds fail <name-or-rank>
```

## Delete

```bash
# ⚠ NGUY HIỂM: Xóa filesystem (nguy hiểm) | Delete filesystem (destructive)
# từ khóa: xóa cephfs
ceph fs rm <fs> --yes-i-really-mean-it
```
