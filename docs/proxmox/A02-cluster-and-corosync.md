# A2 · Cluster and corosync

[← Mục lục](../../README.md) · Proxmox host · 16 lệnh

[← A1 System and node](../proxmox/A01-system-and-node.md) · [A3 Virtual machines (qm) →](../proxmox/A03-virtual-machines-qm.md)

## Status

```bash
# Quorum, votes, links
pvecm status

# Cluster members
pvecm nodes

# Quorum details
corosync-quorumtool -s
```

## Links

```bash
# KNET link status per node
corosync-cfgtool -s

# Node and link list
corosync-cfgtool -n

# Runtime member info
corosync-cmapctl runtime.members
```

## Logs

```bash
# Follow corosync log
journalctl -u corosync -f

# Follow pmxcfs log
journalctl -u pve-cluster -f
```

## Config

```bash
# Cluster config
cat /etc/pve/corosync.conf
```

## Membership

```bash
# Join a node
pvecm add <existing-node-ip> --link0 <ip>

# ⚠ NGUY HIỂM: Remove a node (destructive)
pvecm delnode <node>
```

## Quorum

```bash
# Force expected votes (emergency)
pvecm expected <n>

# Add external QDevice
pvecm qdevice setup <qnetd-ip>

# Remove QDevice
pvecm qdevice remove
```

## Recovery

```bash
# Start pmxcfs in local mode without quorum (emergency)
pmxcfs -l

# Restart cluster stack
systemctl restart pve-cluster corosync
```
