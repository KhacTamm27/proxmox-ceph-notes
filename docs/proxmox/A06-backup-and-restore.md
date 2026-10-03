# A6 · Backup and restore

[← Mục lục](../../README.md) · Proxmox host · 16 lệnh

[← A5 Storage (pvesm)](../proxmox/A05-storage-pvesm.md) · [A7 High availability and replication →](../proxmox/A07-high-availability-and-replication.md)

## vzdump

```bash
# Backup a guest
vzdump <vmid> --storage <storage> --mode snapshot --compress zstd

# Backup all guests on node
vzdump --all --storage <storage>
```

## Restore

```bash
# Restore VM
qmrestore <archive-or-volid> <vmid> --storage <storage>

# Restore container
pct restore <ctid> <archive-or-volid> --storage <storage>
```

## Jobs

```bash
# List backup jobs
pvesh get /cluster/backup
```

## PBS client

```bash
# List backup groups
proxmox-backup-client list --repository <user@realm@host:datastore>

# List snapshots
proxmox-backup-client snapshot list --repository <repo>

# File-level backup
proxmox-backup-client backup <name>.pxar:<path> --repository <repo>

# File-level restore
proxmox-backup-client restore <snapshot> <archive> <target> --repository <repo>
```

## PBS server (on PBS host)

```bash
# List datastores
proxmox-backup-manager datastore list
```

## PBS server

```bash
# Start GC
proxmox-backup-manager garbage-collection start <datastore>

# Verify jobs
proxmox-backup-manager verify-job list

# Prune jobs
proxmox-backup-manager prune-job list

# Sync jobs
proxmox-backup-manager sync-job list

# Disks on PBS host
proxmox-backup-manager disk list

# PBS users
proxmox-backup-manager user list
```
