# A14 · Ceph management from Proxmox (pveceph)

[← Mục lục](../../README.md) · Proxmox host · 16 lệnh

[← A13 Tasks, logs and API](../proxmox/A13-tasks-logs-and-api.md)

## Install

```bash
# Cài gói Ceph | Install Ceph packages
# từ khóa: cài ceph
pveceph install

# Khởi tạo cấu hình Ceph | Initialize Ceph config
# từ khóa: khởi tạo ceph mạng public cluster
pveceph init --network <cidr> --cluster-network <cidr>
```

## MON

```bash
# Tạo MON trên node này | Create MON on this node
# từ khóa: tạo mon
pveceph mon create

# Xóa MON | Remove MON
# từ khóa: xóa mon
pveceph mon destroy <id>
```

## MGR

```bash
# Tạo MGR | Create MGR
# từ khóa: tạo mgr
pveceph mgr create

# Xóa MGR | Remove MGR
# từ khóa: xóa mgr
pveceph mgr destroy <id>
```

## OSD

```bash
# Tạo OSD từ đĩa | Create OSD
# từ khóa: tạo osd thêm đĩa thay đĩa
pveceph osd create /dev/<dev>

# ⚠ NGUY HIỂM: Xóa OSD (nguy hiểm) | Remove OSD (destructive)
# từ khóa: xóa osd thay đĩa destroy
pveceph osd destroy <osd-id> --cleanup
```

## Pool

```bash
# Liệt kê pool | List pools
# từ khóa: pool danh sách
pveceph pool ls

# Tạo pool và storage | Create pool and storage
# từ khóa: tạo pool
pveceph pool create <pool> --size 3 --min_size 2 --crush_rule <rule> --add_storages 1

# Đổi tùy chọn pool | Change pool option
# từ khóa: pool target ratio
pveceph pool set <pool> --target_size_ratio 0.9

# ⚠ NGUY HIỂM: Xóa pool (nguy hiểm) | Delete pool (destructive)
# từ khóa: xóa pool
pveceph pool destroy <pool>
```

## CephFS

```bash
# Tạo MDS | Create MDS
# từ khóa: tạo mds cephfs
pveceph mds create

# Tạo CephFS | Create CephFS
# từ khóa: tạo cephfs
pveceph fs create --name <fs> --add-storage
```

## Services

```bash
# Bật hoặc dừng dịch vụ Ceph trên node | Start or stop Ceph services on node
# từ khóa: start stop ceph service
pveceph start / pveceph stop
```

## Cleanup

```bash
# ⚠ NGUY HIỂM: Xóa cấu hình Ceph khỏi node (nguy hiểm) | Remove Ceph config from node (destructive)
# từ khóa: gỡ ceph purge
pveceph purge
```
