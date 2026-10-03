# A4 · Containers (pct) and templates

[← Mục lục](../../README.md) · Proxmox host · 19 lệnh

[← A3 Virtual machines (qm)](../proxmox/A03-virtual-machines-qm.md) · [A5 Storage (pvesm) →](../proxmox/A05-storage-pvesm.md)

## Inspect

```bash
# List containers
pct list

# Status
pct status <ctid>

# Config
pct config <ctid>
```

## Power

```bash
# Power control
pct start <ctid> / pct shutdown <ctid> / pct stop <ctid>
```

## Access

```bash
# Shell inside container
pct enter <ctid>

# Run command
pct exec <ctid> -- <cmd>

# Copy file in
pct push <ctid> <src> <dst>

# Copy file out
pct pull <ctid> <src> <dst>
```

## Create

```bash
# Create container
pct create <ctid> <template> --storage <storage>

# Clone
pct clone <ctid> <newid>
```

## Config

```bash
# Change resources
pct set <ctid> --memory 2048 --cores 2

# Grow root disk
pct resize <ctid> rootfs +5G

# Remove lock
pct unlock <ctid>
```

## Snapshot

```bash
# Snapshot and roll back
pct snapshot <ctid> <name> / pct rollback <ctid> <name>
```

## Migration

```bash
# Migrate container
pct migrate <ctid> <node> --restart
```

## Delete

```bash
# ⚠ NGUY HIỂM: Delete (destructive)
pct destroy <ctid>
```

## Templates

```bash
# Refresh template list
pveam update

# Available templates
pveam available

# Download template
pveam download <storage> <template>
```
