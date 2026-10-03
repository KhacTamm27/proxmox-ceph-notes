# A7 · High availability and replication

[← Mục lục](../../README.md) · Proxmox host · 14 lệnh

[← A6 Backup and restore](../proxmox/A06-backup-and-restore.md) · [A8 Network →](../proxmox/A08-network.md)

## Status

```bash
# CRM, LRM and resource states
ha-manager status

# Configured HA resources
ha-manager config
```

## Resources

```bash
# Add VM to HA
ha-manager add vm:<vmid> --state started

# Change HA state
ha-manager set vm:<vmid> --state disabled

# Remove from HA
ha-manager remove vm:<vmid>
```

## Groups

```bash
# Create HA group (PVE 8)
ha-manager groupadd <group> --nodes node1:2,node2:1
```

## Move

```bash
# Live migrate an HA VM
ha-manager migrate vm:<vmid> <node>

# Stop, move, start
ha-manager relocate vm:<vmid> <node>
```

## Maintenance

```bash
# Maintenance mode (PVE 8.2+)
ha-manager crm-command node-maintenance enable <node>

# Leave maintenance mode
ha-manager crm-command node-maintenance disable <node>
```

## Services

```bash
# HA daemons
systemctl status pve-ha-crm pve-ha-lrm
```

## Replication

```bash
# Replication jobs
pvesr list

# Replication state
pvesr status

# Create ZFS replication job
pvesr create-local-job <vmid>-<n> <target-node> --schedule "*/15"
```
