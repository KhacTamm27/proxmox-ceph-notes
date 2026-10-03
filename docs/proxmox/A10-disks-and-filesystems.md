# A10 · Disks and filesystems

[← Mục lục](../../README.md) · Proxmox host · 17 lệnh

[← A9 Firewall](../proxmox/A09-firewall.md) · [A11 Hardware and performance →](../proxmox/A11-hardware-and-performance.md)

## Inventory

```bash
# Block devices
lsblk -o NAME,SIZE,TYPE,MODEL,SERIAL,MOUNTPOINT

# UUIDs and filesystems
blkid
```

## Usage

```bash
# Filesystem usage
df -h
```

## NVMe

```bash
# NVMe devices
nvme list

# NVMe health and wear
nvme smart-log /dev/nvme0
```

## SMART

```bash
# SMART data
smartctl -a /dev/<dev>
```

## LVM

```bash
# LVM overview
pvs / vgs / lvs

# LVs with backing devices
lvs -o +devices
```

## ZFS

```bash
# Pool health
zpool status

# Pool capacity
zpool list

# Datasets
zfs list
```

## IO

```bash
# Device latency and utilization
iostat -x 1

# Processes doing IO
iotop -o
```

## Benchmark

```bash
# Basic host benchmark
pveperf

# Disk benchmark
fio --name=t --filename=<file> --rw=randwrite --bs=4k --iodepth=32 --runtime=30 --time_based
```

## Wipe

```bash
# ⚠ NGUY HIỂM: Remove signatures (destructive)
wipefs -a /dev/<dev>

# ⚠ NGUY HIỂM: Wipe partition table (destructive)
sgdisk --zap-all /dev/<dev>
```
