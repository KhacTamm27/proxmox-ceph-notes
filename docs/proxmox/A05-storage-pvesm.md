# A5 · Storage (pvesm)

[← Mục lục](../../README.md) · Proxmox host · 11 lệnh

[← A4 Containers (pct) and templates](../proxmox/A04-containers-pct-and-templates.md) · [A6 Backup and restore →](../proxmox/A06-backup-and-restore.md)

## Status

```bash
# All storages and usage
pvesm status

# Volumes on a storage
pvesm list <storage>
```

## Config

```bash
# Storage definitions
cat /etc/pve/storage.cfg

# Add storage
pvesm add <type> <id> ...

# Change storage options
pvesm set <id> --content images,rootdir

# Remove storage definition
pvesm remove <id>
```

## Scan

```bash
# Discover NFS exports
pvesm scan nfs <server>

# Discover iSCSI targets
pvesm scan iscsi <portal>
```

## Volume

```bash
# Resolve volume path
pvesm path <volume-id>

# Allocate volume
pvesm alloc <storage> <vmid> <name> <size>

# ⚠ NGUY HIỂM: Delete volume (destructive)
pvesm free <volume-id>
```
