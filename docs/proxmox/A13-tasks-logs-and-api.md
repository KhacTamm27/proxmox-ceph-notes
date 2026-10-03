# A13 · Tasks, logs and API

[← Mục lục](../../README.md) · Proxmox host · 10 lệnh

[← A12 Access control (pveum)](../proxmox/A12-access-control-pveum.md) · [A14 Ceph management from Proxmox (pveceph) →](../proxmox/A14-ceph-management-from-proxmox-pveceph.md)

## Tasks

```bash
# Recent tasks
pvenode task list

# Task log
pvenode task log <upid>

# Task state
pvenode task status <upid>
```

## Logs

```bash
# API daemon log
journalctl -u pvedaemon -f

# Web proxy log
journalctl -u pveproxy -f

# System log
tail -f /var/log/syslog
```

## API

```bash
# Cluster status via API
pvesh get /cluster/status

# All VMs in cluster
pvesh get /cluster/resources --type vm

# Node status
pvesh get /nodes/<node>/status

# Start VM via API
pvesh create /nodes/<node>/qemu/<vmid>/status/start
```
