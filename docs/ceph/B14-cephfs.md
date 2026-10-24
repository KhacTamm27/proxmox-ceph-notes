# B14 · CephFS

[← Mục lục](../../README.md) · Ceph · 8 lệnh

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← B13 RGW và S3 (radosgw-admin)](../ceph/B13-rgw-and-s3-radosgw-admin.md) · [B15 Xác thực (cephx) →](../ceph/B15-authentication-cephx.md)

## Trạng thái (Status)

```bash
# [chỉ đọc] Liệt kê CephFS | List filesystems
# từ khóa: cephfs danh sách
ceph fs ls

# [chỉ đọc] Rank, client và dung lượng của CephFS | Ranks, clients, usage
# từ khóa: cephfs mds rank client
ceph fs status

# [chỉ đọc] Trạng thái MDS | MDS states
# từ khóa: mds trạng thái
ceph mds stat

# [chỉ đọc] Bản đồ filesystem | Filesystem map
# từ khóa: cephfs map
ceph fs get <fs>
```

## Tạo mới (Create)

```bash
# Tạo filesystem | Create filesystem
# từ khóa: tạo cephfs
ceph fs new <fs> <metadata-pool> <data-pool>
```

## Subvolume

```bash
# [chỉ đọc] Liệt kê subvolume | List subvolumes
# từ khóa: subvolume
ceph fs subvolume ls <fs>
```

## Chuyển dự phòng (Failover)

```bash
# Ép MDS failover | Fail an MDS
# từ khóa: mds failover treo
ceph mds fail <name-or-rank>
```

## Xóa (Delete)

```bash
# ⚠ NGUY HIỂM: Xóa filesystem (nguy hiểm) | Delete filesystem (destructive)
# từ khóa: xóa cephfs
ceph fs rm <fs> --yes-i-really-mean-it
```

## Case và runbook dùng lệnh trong nhóm này

- [CephFS: MDS failover khi restart hoặc nâng cấp (max_mds lớn hơn 1)](../cases/ceph/cephfs-mds-restart.md)
- [Nâng cấp Ceph Quincy 17.2.8 → Reef 18.2.8 → Squid 19.2.4 trên PVE 8.4 (3 node, có CephFS)](../runbooks/rb-ceph-upgrade-quincy-reef-squid.md)
- [PVE host hỏng đĩa boot, không có backup cấu hình: kiểm kê và dựng lại node](../cases/pve/pve-host-rebuild-no-config-backup.md)
- [Xóa node Proxmox khỏi cluster an toàn (VM, HA và Ceph)](../runbooks/rb-pve-remove-node.md)
