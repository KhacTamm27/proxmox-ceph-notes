# A9 · Firewall

[← Mục lục](../../README.md) · Proxmox host · 5 lệnh

[← A8 Network](../proxmox/A08-network.md) · [A10 Disks and filesystems →](../proxmox/A10-disks-and-filesystems.md)

## Status

```bash
# Firewall state
pve-firewall status

# Detected local networks
pve-firewall localnet
```

## Rules

```bash
# Show generated rules
pve-firewall compile

# Cluster-level rules
cat /etc/pve/firewall/cluster.fw
```

## Control

```bash
# Restart firewall
pve-firewall restart
```
