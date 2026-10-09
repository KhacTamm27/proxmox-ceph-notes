# A5 · Storage (pvesm)

[← Mục lục](../../README.md) · Proxmox host · 11 lệnh

[← A4 Containers (pct) and templates](../proxmox/A04-containers-pct-and-templates.md) · [A6 Backup and restore →](../proxmox/A06-backup-and-restore.md)

## Status

```bash
# Xem tất cả storage và mức sử dụng | All storages and usage
# từ khóa: storage dung lượng đầy offline unknown dấu hỏi nfs treo
pvesm status

# Liệt kê volume trong storage | Volumes on a storage
# từ khóa: volume danh sách đĩa trong storage
pvesm list <storage>
```

## Config

```bash
# Xem định nghĩa các storage | Storage definitions
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

## Scan

```bash
# Dò các export NFS của server | Discover NFS exports
# từ khóa: nfs export dò tìm
pvesm scan nfs <server>

# Dò các target iSCSI | Discover iSCSI targets
# từ khóa: iscsi target dò tìm
pvesm scan iscsi <portal>
```

## Volume

```bash
# Xem đường dẫn thực của volume | Resolve volume path
# từ khóa: đường dẫn volume path
pvesm path <volume-id>

# Tạo (cấp phát) volume mới | Allocate volume
# từ khóa: cấp phát volume tạo đĩa
pvesm alloc <storage> <vmid> <name> <size>

# ⚠ NGUY HIỂM: Xóa volume (nguy hiểm) | Delete volume (destructive)
# từ khóa: xóa volume đĩa mồ côi free
pvesm free <volume-id>
```
