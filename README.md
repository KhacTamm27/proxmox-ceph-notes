# Proxmox + Ceph command notes

Tài liệu cá nhân: 493 lệnh, 32 nhóm. Lệnh có ⚠ (23 lệnh) là lệnh phá hủy hoặc ảnh hưởng dịch vụ, đọc kỹ trước khi chạy.

## Cách tìm nhanh

- Biết tên nhóm: bấm vào mục lục bên dưới, hoặc mở mindmap kèm `#B13` (ví dụ `.../#B13` mở thẳng RGW).
- Biết từ khóa: mở mindmap, nhấn `/` rồi gõ. Link `.../?q=scrub` mở sẵn kết quả lọc.
- Trên GitHub: nhấn `t` để tìm file theo tên, nhấn `/` để tìm trong repo (gõ `crush`, `radosgw-admin user`).
- Trong một file .md: nút Outline (góc phải trên) nhảy giữa các mục con, mỗi khối lệnh có nút copy.

## Case study (lỗi và cách xử lý)

| Sự cố | Triệu chứng |
|---|---|
| [OSD down hoặc up/down liên tục (flapping)](docs/cases/osd-down-flapping.md) | ceph -s báo "N osds down", OSD lúc up lúc down, log có "wrongly marked me down" hoặc heartbeat_check no reply. |
| [PG inconsistent / scrub errors](docs/cases/pg-inconsistent.md) | HEALTH_ERR, "pg x.y is active+clean+inconsistent", "N scrub errors". |
| [Clock skew trên MON (lệch giờ)](docs/cases/clock-skew.md) | HEALTH_WARN "clock skew detected on mon.X", MON mất quorum chập chờn. |
| [Cluster Proxmox mất quorum](docs/cases/pve-quorum-lost.md) | GUI báo "cluster not ready - no quorum", /etc/pve chuyển read-only, không start được VM, node hiện đỏ. |
| [Ceph nearfull / full / pool đầy](docs/cases/nearfull-full.md) | HEALTH_WARN "N osd(s) nearfull", HEALTH_ERR "full osd(s)", client không ghi được, backfill dừng. |
| [Slow ops / blocked requests](docs/cases/slow-ops.md) | HEALTH_WARN "N slow ops", VM đơ hoặc IO chậm, "requests are blocked". |
| [Thay đĩa OSD hỏng](docs/cases/osd-replace-disk.md) | OSD down kéo dài, SMART báo lỗi hoặc dmesg có I/O error, cần thay đĩa vật lý. |
| [Bảo trì hoặc reboot một node Proxmox + Ceph](docs/cases/node-maintenance.md) | Cần reboot node để nâng cấp kernel hoặc thay phần cứng mà không làm gián đoạn VM và không kích hoạt rebalance. |
| [PG degraded / undersized, recovery chậm](docs/cases/pg-degraded-recovery.md) | HEALTH_WARN "Degraded data redundancy", "N pgs undersized/degraded", "objects misplaced", recovery chạy lâu. |
| [Large omap objects (thường do bucket index RGW)](docs/cases/large-omap.md) | HEALTH_WARN "N large omap objects". |
| [RGW/S3 trả 503 hoặc timeout, upload lỗi](docs/cases/rgw-503.md) | Client S3 nhận 503/timeout, upload thất bại, RGW phản hồi chậm. |
| [MON down, ceph -s treo hoặc mất quorum Ceph](docs/cases/mon-down.md) | ceph -s đứng treo hoặc báo "1/3 mons down", "mon.X is down". |
| [VM bị lock (backup/snapshot), không start hoặc migrate được](docs/cases/vm-locked.md) | Báo "VM is locked (backup)" hoặc "(snapshot)", không start, stop, migrate hoặc xóa được. |
| [GUI Proxmox bị đăng xuất liên tục hoặc không đăng nhập được](docs/cases/pve-gui-logout.md) | GUI bị đá ra sau một thời gian ngắn, báo "permission denied" hoặc "invalid ticket", trang tải chậm hoặc treo. |
| [Node Proxmox đầy ổ root, dịch vụ lỗi](docs/cases/pve-disk-full.md) | "No space left on device", dịch vụ không start, không ghi được /etc/pve, GUI lỗi. |

## Proxmox host

| ID | Nhóm | Lệnh | Gồm |
|---|---|---:|---|
| A1 | [System and node](docs/proxmox/A01-system-and-node.md) | 21 | Version, Load, Time, Services, Node, Certificates, Upgrade, Kernel |
| A2 | [Cluster and corosync](docs/proxmox/A02-cluster-and-corosync.md) | 16 | Status, Links, Logs, Config, Membership, Quorum, Recovery |
| A3 | [Virtual machines (qm)](docs/proxmox/A03-virtual-machines-qm.md) | 39 | Inspect, Power, Create, Config, Snapshot, Migration, Guest agent, Console, Cloud-init, Import |
| A4 | [Containers (pct) and templates](docs/proxmox/A04-containers-pct-and-templates.md) | 19 | Inspect, Power, Access, Create, Config, Snapshot, Migration, Delete, Templates |
| A5 | [Storage (pvesm)](docs/proxmox/A05-storage-pvesm.md) | 11 | Status, Config, Scan, Volume |
| A6 | [Backup and restore](docs/proxmox/A06-backup-and-restore.md) | 16 | vzdump, Restore, Jobs, PBS client, PBS server (on PBS host), PBS server |
| A7 | [High availability and replication](docs/proxmox/A07-high-availability-and-replication.md) | 14 | Status, Resources, Groups, Move, Maintenance, Services, Replication |
| A8 | [Network](docs/proxmox/A08-network.md) | 23 | Interfaces, Bridge, Bond, Config, NIC, MTU test, Throughput, Sockets, Capture, Path, Neighbors, OVS, QoS |
| A9 | [Firewall](docs/proxmox/A09-firewall.md) | 5 | Status, Rules, Control |
| A10 | [Disks and filesystems](docs/proxmox/A10-disks-and-filesystems.md) | 17 | Inventory, Usage, NVMe, SMART, LVM, ZFS, IO, Benchmark, Wipe |
| A11 | [Hardware and performance](docs/proxmox/A11-hardware-and-performance.md) | 13 | CPU, Memory, Load, Sensors, BMC, Kernel log |
| A12 | [Access control (pveum)](docs/proxmox/A12-access-control-pveum.md) | 8 | Users, Roles, Permissions, Tokens, Realms |
| A13 | [Tasks, logs and API](docs/proxmox/A13-tasks-logs-and-api.md) | 10 | Tasks, Logs, API |
| A14 | [Ceph management from Proxmox (pveceph)](docs/proxmox/A14-ceph-management-from-proxmox-pveceph.md) | 16 | Install, MON, MGR, OSD, Pool, CephFS, Services, Cleanup |

## Ceph

| ID | Nhóm | Lệnh | Gồm |
|---|---|---:|---|
| B1 | [Health and status](docs/ceph/B01-health-and-status.md) | 14 | Overview, Health, Capacity, Versions, Log, Crash, Time, Report |
| B2 | [MON](docs/ceph/B02-mon.md) | 8 | Status, Quorum, Admin socket, Maintenance, Features, Protocol, Map |
| B3 | [MGR and modules](docs/ceph/B03-mgr-and-modules.md) | 12 | Status, Control, Modules, Balancer, IO, Progress |
| B4 | [OSD status](docs/ceph/B04-osd-status.md) | 16 | Tree, Usage, State, Info, Perf, Ratios, Blocklist |
| B5 | [OSD flags and maintenance](docs/ceph/B05-osd-flags-and-maintenance.md) | 15 | Flags, Per subtree, Safety, State, Weight |
| B6 | [OSD lifecycle and devices](docs/ceph/B06-osd-lifecycle-and-devices.md) | 15 | Inventory, Create, Replace, Remove, Wipe, Service, BlueStore, Maintenance, Class |
| B7 | [OSD daemon and performance (admin socket)](docs/ceph/B07-osd-daemon-and-performance-admin-socket.md) | 9 | Ops, Perf, Config, Bench, Heartbeat |
| B8 | [CRUSH map](docs/ceph/B08-crush-map.md) | 19 | View, Rules, Buckets, Map file |
| B9 | [Pools](docs/ceph/B09-pools.md) | 18 | View, Create, Settings, Autoscale, Quota, Rename, Delete, Usage |
| B10 | [Placement groups](docs/ceph/B10-placement-groups.md) | 16 | Summary, List, Mapping, Detail, Scrub, Repair, Priority, Upmap |
| B11 | [Recovery, scrub and config tuning](docs/ceph/B11-recovery-scrub-and-config-tuning.md) | 11 | Config, Backfill, Recovery, mClock, Scrub |
| B12 | [RBD (VM disks)](docs/ceph/B12-rbd-vm-disks.md) | 26 | List, Info, Snapshot, Clone, Copy, Resize, Space, Trash, Delete, Perf, Bench, Mapping |
| B13 | [RGW and S3 (radosgw-admin)](docs/ceph/B13-rgw-and-s3-radosgw-admin.md) | 33 | Service, Users, Keys, Subuser, Quota, Buckets, Reshard, Usage, Lifecycle, GC, Topology, Index pool |
| B14 | [CephFS](docs/ceph/B14-cephfs.md) | 8 | Status, Create, Subvolume, Failover, Delete |
| B15 | [Authentication (cephx)](docs/ceph/B15-authentication-cephx.md) | 6 | List, Show, Create, Change, Delete |
| B16 | [Benchmarks and low-level rados](docs/ceph/B16-benchmarks-and-low-level-rados.md) | 12 | Bench, Objects, Omap |
| B17 | [Upgrade and compatibility](docs/ceph/B17-upgrade-and-compatibility.md) | 8 | Versions, Release, Clients, Pre-upgrade, Post-upgrade |
| B18 | [Troubleshooting shortlist](docs/ceph/B18-troubleshooting-shortlist.md) | 19 | HEALTH_WARN, Slow ops, OSD flapping, PGs stuck, Undersized, Nearfull, Large omap, Clock skew, MON down, Client hang |

## Cập nhật tài liệu

- `data/commands.json`: nhóm → nhóm con → `{c: lệnh, p: mô tả, d: nguy hiểm?}`.
- `data/vi.json`: mô tả tiếng Việt và từ khóa, khóa là đúng chuỗi lệnh trong commands.json: `"lệnh": ["mô tả", "từ khóa"]`.
- `data/cases.json`: các case study (triệu chứng, nguyên nhân, các bước, lưu ý).

Sau khi sửa, chạy:

```bash
python3 scripts/build.py --repo <user>/<repo>
```

Lệnh trên sinh lại README này, toàn bộ `docs/**/*.md` và `docs/index.html`.
