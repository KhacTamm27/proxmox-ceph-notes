# A6 · Backup and restore

[← Mục lục](../../README.md) · Proxmox host · 16 lệnh

[← A5 Storage (pvesm)](../proxmox/A05-storage-pvesm.md) · [A7 High availability and replication →](../proxmox/A07-high-availability-and-replication.md)

## vzdump

```bash
# Backup một VM hoặc container | Backup a guest
# từ khóa: backup sao lưu vzdump
vzdump <vmid> --storage <storage> --mode snapshot --compress zstd

# Backup tất cả guest trên node | Backup all guests on node
# từ khóa: backup tất cả
vzdump --all --storage <storage>
```

## Restore

```bash
# Restore VM từ backup | Restore VM
# từ khóa: restore khôi phục vm
qmrestore <archive-or-volid> <vmid> --storage <storage>

# Restore container từ backup | Restore container
# từ khóa: restore khôi phục container
pct restore <ctid> <archive-or-volid> --storage <storage>
```

## Jobs

```bash
# Liệt kê các job backup | List backup jobs
# từ khóa: job backup lịch
pvesh get /cluster/backup
```

## PBS client

```bash
# Liệt kê nhóm backup trên PBS | List backup groups
# từ khóa: pbs backup danh sách
proxmox-backup-client list --repository <user@realm@host:datastore>

# Liệt kê snapshot backup trên PBS | List snapshots
# từ khóa: pbs snapshot
proxmox-backup-client snapshot list --repository <repo>

# Backup file/thư mục lên PBS | File-level backup
# từ khóa: pbs backup file thư mục pxar
proxmox-backup-client backup <name>.pxar:<path> --repository <repo>

# Restore file/thư mục từ PBS | File-level restore
# từ khóa: pbs restore file
proxmox-backup-client restore <snapshot> <archive> <target> --repository <repo>
```

## PBS server (on PBS host)

```bash
# Liệt kê datastore của PBS | List datastores
# từ khóa: pbs datastore
proxmox-backup-manager datastore list
```

## PBS server

```bash
# Chạy dọn rác (GC) cho datastore | Start GC
# từ khóa: pbs gc dọn rác giải phóng dung lượng
proxmox-backup-manager garbage-collection start <datastore>

# Liệt kê job verify | Verify jobs
# từ khóa: pbs verify kiểm tra toàn vẹn
proxmox-backup-manager verify-job list

# Liệt kê job prune | Prune jobs
# từ khóa: pbs prune giữ lại bản backup
proxmox-backup-manager prune-job list

# Liệt kê job sync | Sync jobs
# từ khóa: pbs sync đồng bộ
proxmox-backup-manager sync-job list

# Liệt kê đĩa trên máy PBS | Disks on PBS host
# từ khóa: pbs đĩa
proxmox-backup-manager disk list

# Liệt kê user PBS | PBS users
# từ khóa: pbs user
proxmox-backup-manager user list
```
