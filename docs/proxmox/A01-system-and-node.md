# A1 · System and node

[← Mục lục](../../README.md) · Proxmox host · 21 lệnh

[A2 Cluster and corosync →](../proxmox/A02-cluster-and-corosync.md)

## Version

```bash
# PVE and package versions
pveversion -v

# Hostname, OS
hostnamectl

# Running kernel
uname -r
```

## Load

```bash
# Uptime and load
uptime
```

## Time

```bash
# Time zone and sync state
timedatectl

# Độ lệch NTP trên máy hiện tại | NTP offset
# từ khóa: ntp chrony lệch giờ clock skew
chronyc tracking

# NTP sources
chronyc sources -v
```

## Services

```bash
# Failed units
systemctl --failed

# Core PVE services
systemctl status pve-cluster pvedaemon pveproxy pvestatd pve-firewall pvescheduler
```

## Node

```bash
# Node config
pvenode config get

# Start all guests on node
pvenode startall

# Stop all guests on node
pvenode stopall

# Migrate all guests away
pvenode migrateall <target-node>
```

## Certificates

```bash
# Certificate details
pvenode cert info

# Regenerate cluster certificates
pvecm updatecerts --force
```

## Upgrade

```bash
# Refresh package lists
apt update

# Upgrade packages
apt full-upgrade

# Pre-upgrade checker (PVE 8 to 9)
pve8to9 --full
```

## Kernel

```bash
# Boot setup status
proxmox-boot-tool status

# Installed kernels
proxmox-boot-tool kernel list

# Pin default kernel
proxmox-boot-tool kernel pin <version>
```
