# A10 · Disks and filesystems

[← Mục lục](../../README.md) · Proxmox host · 17 lệnh

[← A9 Firewall](../proxmox/A09-firewall.md) · [A11 Hardware and performance →](../proxmox/A11-hardware-and-performance.md)

## Inventory

```bash
# Liệt kê thiết bị khối, model và serial | Block devices
# từ khóa: đĩa ổ cứng model serial lsblk
lsblk -o NAME,SIZE,TYPE,MODEL,SERIAL,MOUNTPOINT

# Xem UUID và kiểu filesystem | UUIDs and filesystems
# từ khóa: uuid filesystem blkid
blkid
```

## Usage

```bash
# Dung lượng các filesystem | Filesystem usage
# từ khóa: đầy disk đầy ổ dung lượng root
df -h
```

## NVMe

```bash
# Liệt kê ổ NVMe | NVMe devices
# từ khóa: nvme ổ
nvme list

# Sức khỏe và độ mòn của NVMe | NVMe health and wear
# từ khóa: nvme smart mòn wear sức khỏe
nvme smart-log /dev/nvme0
```

## SMART

```bash
# Xem dữ liệu SMART của đĩa | SMART data
# từ khóa: smart đĩa hỏng bad sector sức khỏe
smartctl -a /dev/<dev>
```

## LVM

```bash
# Tổng quan LVM (PV, VG, LV) | LVM overview
# từ khóa: lvm pv vg lv
pvs / vgs / lvs

# LV kèm thiết bị phía sau | LVs with backing devices
# từ khóa: lvm thiết bị
lvs -o +devices
```

## ZFS

```bash
# Sức khỏe ZFS pool | Pool health
# từ khóa: zfs pool degraded lỗi
zpool status

# Dung lượng ZFS pool | Pool capacity
# từ khóa: zfs pool dung lượng
zpool list

# Liệt kê dataset ZFS | Datasets
# từ khóa: zfs dataset
zfs list
```

## IO

```bash
# Độ trễ và mức dùng của đĩa theo thời gian thực | Device latency and utilization
# từ khóa: io đĩa chậm latency util
iostat -x 1

# Tiến trình đang dùng IO | Processes doing IO
# từ khóa: io tiến trình nặng
iotop -o
```

## Benchmark

```bash
# Benchmark cơ bản của host | Basic host benchmark
# từ khóa: benchmark hiệu năng host
pveperf

# Benchmark đĩa bằng fio | Disk benchmark
# từ khóa: benchmark fio đĩa iops
fio --name=t --filename=<file> --rw=randwrite --bs=4k --iodepth=32 --runtime=30 --time_based
```

## Wipe

```bash
# ⚠ NGUY HIỂM: Xóa chữ ký filesystem (nguy hiểm) | Remove signatures (destructive)
# từ khóa: xóa đĩa wipe tái sử dụng đĩa
wipefs -a /dev/<dev>

# ⚠ NGUY HIỂM: Xóa bảng phân vùng (nguy hiểm) | Wipe partition table (destructive)
# từ khóa: xóa phân vùng zap gpt
sgdisk --zap-all /dev/<dev>
```
