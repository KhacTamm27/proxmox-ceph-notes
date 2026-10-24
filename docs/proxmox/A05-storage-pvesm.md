# A5 · Storage (pvesm)

[← Mục lục](../../README.md) · Proxmox host · 11 lệnh

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← A4 Container (pct) và template](../proxmox/A04-containers-pct-and-templates.md) · [A6 Backup và khôi phục →](../proxmox/A06-backup-and-restore.md)

## Trạng thái (Status)

```bash
# [chỉ đọc] Xem tất cả storage và mức sử dụng | All storages and usage
# từ khóa: storage dung lượng đầy offline unknown dấu hỏi nfs treo
pvesm status

# [chỉ đọc] Liệt kê volume trong storage | Volumes on a storage
# từ khóa: volume danh sách đĩa trong storage
pvesm list <storage>
```

## Cấu hình (Config)

```bash
# [chỉ đọc] Xem định nghĩa các storage | Storage definitions
# từ khóa: storage config cấu hình
cat /etc/pve/storage.cfg

# Thêm storage | Add storage
# từ khóa: thêm storage mới
pvesm add <type> <id> ...

# Đổi tùy chọn storage (loại nội dung) | Change storage options
# từ khóa: content loại nội dung storage
pvesm set <id> --content images,rootdir

# Gỡ định nghĩa storage | Remove storage definition
# từ khóa: xóa storage remove
pvesm remove <id>
```

## Dò tìm (Scan)

```bash
# [chỉ đọc] Dò các export NFS của server | Discover NFS exports
# từ khóa: nfs export dò tìm
pvesm scan nfs <server>

# [chỉ đọc] Dò các target iSCSI | Discover iSCSI targets
# từ khóa: iscsi target dò tìm
pvesm scan iscsi <portal>
```

## Volume

```bash
# [chỉ đọc] Xem đường dẫn thực của volume | Resolve volume path
# từ khóa: đường dẫn volume path
pvesm path <volume-id>

# Tạo (cấp phát) volume mới | Allocate volume
# từ khóa: cấp phát volume tạo đĩa
pvesm alloc <storage> <vmid> <name> <size>

# ⚠ NGUY HIỂM: Xóa volume (nguy hiểm) | Delete volume (destructive)
# từ khóa: xóa volume đĩa mồ côi free
pvesm free <volume-id>
```

## Case và runbook dùng lệnh trong nhóm này

- [Storage dùng chung giữa hai cluster Proxmox gây xung đột lock/VMID](../cases/pve/pve-storage-shared-clusters.md)
- [Node Proxmox đầy ổ root, dịch vụ lỗi](../cases/pve/pve-disk-full.md)
- [Migrate VM thất bại](../cases/pve/migrate-fail.md)
- [VM không start được](../cases/pve/vm-wont-start.md)
- [HA: VM không tự chạy lại trên node khác, trạng thái error hoặc fence](../cases/pve/ha-no-restart.md)
- [Backup vzdump lỗi hoặc treo](../cases/pve/backup-fail.md)
- [local-lvm (thin pool) đầy](../cases/pve/lvm-thin-full.md)
- [SAN iSCSI + Shared LVM cho cluster Proxmox, và mở rộng dung lượng online (pvmove)](../runbooks/rb-san-iscsi-shared-lvm.md)
- [NAS NFS làm storage dùng chung cho cluster Proxmox](../runbooks/rb-nas-nfs-storage.md)
- [LUN iSCSI mới hoặc Volume Group không hiện trên một số node (Shared LVM)](../cases/pve/lun-not-visible.md)
- [PVE host hỏng đĩa boot, không có backup cấu hình: kiểm kê và dựng lại node](../cases/pve/pve-host-rebuild-no-config-backup.md)
- [Proxmox ZFS replication: cấu hình và kiểm thử khôi phục VM](../runbooks/rb-pve-zfs-replication.md)
- [V2V Hyper-V sang Proxmox bằng StarWind V2V Converter](../runbooks/rb-v2v-hyperv.md)
- [V2V VMware ESXi sang Proxmox bằng StarWind V2V Converter](../runbooks/rb-v2v-esxi.md)
- [Di chuyển VM giữa hai cluster Proxmox bằng remote migration](../runbooks/rb-pve-cross-cluster-migrate.md)
- [Xóa node Proxmox khỏi cluster an toàn (VM, HA và Ceph)](../runbooks/rb-pve-remove-node.md)
