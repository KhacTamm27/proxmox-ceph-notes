# A3 · Virtual machines (qm)

[← Mục lục](../../README.md) · Proxmox host · 39 lệnh

[← A2 Cluster and corosync](../proxmox/A02-cluster-and-corosync.md) · [A4 Containers (pct) and templates →](../proxmox/A04-containers-pct-and-templates.md)

## Inspect

```bash
# List VMs on node
qm list

# Detailed VM status
qm status <vmid> --verbose

# VM config
qm config <vmid>

# Pending config changes
qm pending <vmid>

# Show KVM command line
qm showcmd <vmid> --pretty
```

## Power

```bash
# Start
qm start <vmid>

# Clean shutdown
qm shutdown <vmid> --timeout 60

# Hard stop
qm stop <vmid>

# Reboot
qm reboot <vmid>

# Hard reset
qm reset <vmid>

# Suspend and resume
qm suspend <vmid> / qm resume <vmid>
```

## Create

```bash
# Create VM
qm create <vmid> --name <n> --memory 4096 --cores 2 --net0 virtio,bridge=vmbr0

# Full clone
qm clone <vmid> <newid> --full

# Convert to template
qm template <vmid>

# ⚠ NGUY HIỂM: Delete VM (destructive)
qm destroy <vmid> --purge
```

## Config

```bash
# Change CPU and RAM
qm set <vmid> --memory 8192 --cores 4

# Add disk
qm set <vmid> --scsi1 <storage>:<size-GiB>

# Grow disk
qm resize <vmid> scsi0 +10G

# Move disk to another storage (alias `qm move-disk`)
qm disk move <vmid> scsi0 <storage>

# Rescan volumes and fix config
qm rescan

# Remove stuck lock
qm unlock <vmid>
```

## Snapshot

```bash
# Create snapshot
qm snapshot <vmid> <name>

# List snapshots
qm listsnapshot <vmid>

# Roll back
qm rollback <vmid> <name>

# Delete snapshot
qm delsnapshot <vmid> <name>
```

## Migration

```bash
# Live migration
qm migrate <vmid> <node> --online

# Live migration with local disks
qm migrate <vmid> <node> --online --with-local-disks
```

## Guest agent

```bash
# Check agent
qm agent <vmid> ping

# Run command in guest
qm guest exec <vmid> -- <cmd>

# Guest IPs
qm guest cmd <vmid> network-get-interfaces
```

## Console

```bash
# Serial console
qm terminal <vmid>

# QEMU monitor
qm monitor <vmid>

# Send key
qm sendkey <vmid> ctrl-alt-delete
```

## Cloud-init

```bash
# Show generated user-data
qm cloudinit dump <vmid> user

# Set cloud-init values
qm set <vmid> --ciuser <u> --sshkeys <file> --ipconfig0 ip=dhcp
```

## Import

```bash
# Add ESXi import source (PVE 8.2+)
pvesm add esxi <id> --server <host> --username <u> --password <p>

# Import OVF
qm importovf <vmid> <file.ovf> <storage>

# Import disk image
qm importdisk <vmid> <disk-file> <storage>

# Convert VMware disk
qemu-img convert -f vmdk -O raw <src.vmdk> <dst.raw>
```
