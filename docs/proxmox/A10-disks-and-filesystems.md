# A10 · Ổ đĩa và filesystem

[← Mục lục](../../README.md) · Proxmox host · 17 lệnh · tên gốc: Disks and filesystems

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← A9 Tường lửa](../proxmox/A09-firewall.md) · [A11 Phần cứng và hiệu năng →](../proxmox/A11-hardware-and-performance.md)

## Kiểm kê (Inventory)

```bash
# [chỉ đọc] Liệt kê thiết bị khối, model và serial | Block devices
# từ khóa: đĩa ổ cứng model serial lsblk
lsblk -o NAME,SIZE,TYPE,MODEL,SERIAL,MOUNTPOINT

# [chỉ đọc] Xem UUID và kiểu filesystem | UUIDs and filesystems
# từ khóa: uuid filesystem blkid
blkid
```

## Mức sử dụng (Usage)

```bash
# [chỉ đọc] Dung lượng các filesystem | Filesystem usage
# từ khóa: đầy disk đầy ổ dung lượng root no space left on device hết
df -h
```

## NVMe

```bash
# [chỉ đọc] Liệt kê ổ NVMe | NVMe devices
# từ khóa: nvme ổ
nvme list

# [chỉ đọc] Sức khỏe và độ mòn của NVMe | NVMe health and wear
# từ khóa: nvme smart mòn wear sức khỏe
nvme smart-log /dev/nvme0
```

## SMART

```bash
# [chỉ đọc] Xem dữ liệu SMART của đĩa | SMART data
# từ khóa: smart đĩa hỏng bad sector sức khỏe ổ cứng sắp reallocated pending
smartctl -a /dev/<dev>
```

## LVM

```bash
# [chỉ đọc] Tổng quan LVM (PV, VG, LV) | LVM overview
# từ khóa: lvm pv vg lv
pvs / vgs / lvs

# [chỉ đọc] LV kèm thiết bị phía sau | LVs with backing devices
# từ khóa: lvm thiết bị
lvs -o +devices
```

## ZFS

```bash
# [chỉ đọc] Sức khỏe ZFS pool | Pool health
# từ khóa: zfs pool degraded lỗi
zpool status

# [chỉ đọc] Dung lượng ZFS pool | Pool capacity
# từ khóa: zfs pool dung lượng
zpool list

# [chỉ đọc] Liệt kê dataset ZFS | Datasets
# từ khóa: zfs dataset
zfs list
```

## IO

```bash
# [chỉ đọc] Độ trễ và mức dùng của đĩa theo thời gian thực | Device latency and utilization
# từ khóa: io đĩa chậm latency util iowait wait await ổ storage
iostat -x 1

# [chỉ đọc] Tiến trình đang dùng IO | Processes doing IO
# từ khóa: io tiến trình nặng
iotop -o
```

## Đo hiệu năng (Benchmark)

```bash
# Benchmark cơ bản của host | Basic host benchmark
# từ khóa: benchmark hiệu năng host
pveperf

# Benchmark đĩa bằng fio | Disk benchmark
# từ khóa: benchmark fio đĩa iops
fio --name=t --filename=<file> --rw=randwrite --bs=4k --iodepth=32 --runtime=30 --time_based
```

## Xóa sạch đĩa (Wipe)

```bash
# ⚠ NGUY HIỂM: Xóa chữ ký filesystem (nguy hiểm) | Remove signatures (destructive)
# từ khóa: xóa đĩa wipe tái sử dụng đĩa
wipefs -a /dev/<dev>

# ⚠ NGUY HIỂM: Xóa bảng phân vùng (nguy hiểm) | Wipe partition table (destructive)
# từ khóa: xóa phân vùng zap gpt
sgdisk --zap-all /dev/<dev>
```

## Case và runbook dùng lệnh trong nhóm này

- [MON down, ceph -s treo hoặc mất quorum Ceph](../cases/ceph/mon-down.md)
- [Node Proxmox đầy ổ root, dịch vụ lỗi](../cases/pve/pve-disk-full.md)
- [Backup vzdump lỗi hoặc treo](../cases/pve/backup-fail.md)
- [OSD down hoặc up/down liên tục (flapping)](../cases/ceph/osd-down-flapping.md)
- [PG inconsistent / scrub errors](../cases/ceph/pg-inconsistent.md)
- [Thay đĩa OSD hỏng](../cases/ceph/osd-replace-disk.md)
- [Ceph cảnh báo OSD device có nguy cơ hỏng](../cases/ceph/osd-device-health-warning.md)
- [Latency OSD cao, IOPS thấp do SSD consumer (không có PLP)](../cases/ceph/osd-latency-consumer-ssd.md)
- [local-lvm (thin pool) đầy](../cases/pve/lvm-thin-full.md)
- [SAN iSCSI + Shared LVM cho cluster Proxmox, và mở rộng dung lượng online (pvmove)](../runbooks/rb-san-iscsi-shared-lvm.md)
- [LUN iSCSI mới hoặc Volume Group không hiện trên một số node (Shared LVM)](../cases/pve/lun-not-visible.md)
- [Nâng cấp một node Proxmox VE từ 5.4 lên 8.x (qua 6, 7, 8) kèm ZFS](../runbooks/rb-pve5-to-8-single.md)
- [ZFS: chọn RAID/vdev và tạo pool cho Proxmox](../runbooks/rb-zfs-vdev-layout.md)
- [ZFS RAIDZ: mở rộng vdev bằng cách gắn thêm disk](../runbooks/rb-zfs-raidz-expansion.md)
- [ZFS: thêm hoặc gỡ L2ARC cache và hot spare](../runbooks/rb-zfs-cache-spare.md)
- [Proxmox boot ZFS mirror: kiểm tra trước khi thay disk rpool](../runbooks/rb-zfs-rpool-replace.md)
- [Proxmox ZFS replication: cấu hình và kiểm thử khôi phục VM](../runbooks/rb-pve-zfs-replication.md)
- [V2V VMware ESXi sang Proxmox bằng StarWind V2V Converter](../runbooks/rb-v2v-esxi.md)
- [PBS S3: ENOENT hoặc Permission denied với cache, không thấy backup](../cases/pve/pbs-s3-permission.md)
- [Slow ops / blocked requests (Ceph chậm, IO bị chặn)](../cases/ceph/slow-ops.md)
