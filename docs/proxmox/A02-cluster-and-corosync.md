# A2 · Cluster và corosync

[← Mục lục](../../README.md) · Proxmox host · 16 lệnh · tên gốc: Cluster and corosync

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← A1 Hệ thống và node](../proxmox/A01-system-and-node.md) · [A3 Máy ảo (qm) →](../proxmox/A03-virtual-machines-qm.md)

## Trạng thái (Status)

```bash
# [chỉ đọc] Xem quorum, số phiếu và link của cluster Proxmox | Quorum, votes, links
# từ khóa: quorum mất quorum no quorum cluster vote
pvecm status

# [chỉ đọc] Liệt kê các node trong cluster | Cluster members
# từ khóa: node thành viên danh sách
pvecm nodes

# [chỉ đọc] Chi tiết quorum theo corosync | Quorum details
# từ khóa: quorum votes
corosync-quorumtool -s
```

## Link mạng cluster (Links)

```bash
# [chỉ đọc] Trạng thái từng link knet giữa các node, phát hiện link đứt | KNET link status per node
# từ khóa: link down mạng cluster knet đứt
corosync-cfgtool -s

# [chỉ đọc] Danh sách node và link corosync | Node and link list
# từ khóa: node link
corosync-cfgtool -n

# [chỉ đọc] Thành viên corosync đang chạy thực tế | Runtime member info
# từ khóa: members runtime
corosync-cmapctl runtime.members
```

## Log (Logs)

```bash
# [chỉ đọc] Theo dõi log corosync theo thời gian thực | Follow corosync log
# từ khóa: log corosync retransmit token lost link
journalctl -u corosync -f

# [chỉ đọc] Theo dõi log pmxcfs (thư mục /etc/pve) | Follow pmxcfs log
# từ khóa: log pmxcfs etc/pve read-only
journalctl -u pve-cluster -f
```

## Cấu hình (Config)

```bash
# [chỉ đọc] Xem cấu hình corosync của cluster | Cluster config
# từ khóa: config corosync
cat /etc/pve/corosync.conf
```

## Thành viên (Membership)

```bash
# Thêm node mới vào cluster (chạy trên node mới) | Join a node
# từ khóa: join thêm node
pvecm add <existing-node-ip> --link0 <ip>

# ⚠ NGUY HIỂM: Xóa node khỏi cluster (nguy hiểm, node phải tắt hẳn trước) | Remove a node (destructive)
# từ khóa: xóa node remove node
pvecm delnode <node>
```

## Quorum

```bash
# Ép số phiếu kỳ vọng khi mất quorum (khẩn cấp, dễ split-brain) | Force expected votes (emergency)
# từ khóa: mất quorum emergency expected votes
pvecm expected <n>

# Thêm QDevice ngoài để cluster 2 node có quorum | Add external QDevice
# từ khóa: qdevice 2 node tie breaker
pvecm qdevice setup <qnetd-ip>

# Gỡ QDevice khỏi cluster | Remove QDevice
# từ khóa: qdevice
pvecm qdevice remove
```

## Phục hồi (Recovery)

```bash
# Chạy pmxcfs chế độ local khi không có quorum (biện pháp cuối) | Start pmxcfs in local mode without quorum (emergency)
# từ khóa: không quorum sửa etc/pve local mode
pmxcfs -l

# Khởi động lại stack cluster khi treo hoặc lệch trạng thái | Restart cluster stack
# từ khóa: restart cluster corosync treo
systemctl restart pve-cluster corosync
```

## Case và runbook dùng lệnh trong nhóm này

- [Cluster Proxmox mất quorum](../cases/pve/pve-quorum-lost.md)
- [Storage dùng chung giữa hai cluster Proxmox gây xung đột lock/VMID](../cases/pve/pve-storage-shared-clusters.md)
- [Bảo trì hoặc reboot một node Proxmox + Ceph](../cases/pve/node-maintenance.md)
- [GUI Proxmox bị đăng xuất liên tục hoặc không đăng nhập được](../cases/pve/pve-gui-logout.md)
- [Migrate VM thất bại](../cases/pve/migrate-fail.md)
- [VM không start được](../cases/pve/vm-wont-start.md)
- [HA: VM không tự chạy lại trên node khác, trạng thái error hoặc fence](../cases/pve/ha-no-restart.md)
- [Corosync link chập chờn, retransmit, node tự reboot (HA watchdog)](../cases/pve/corosync-flapping.md)
- [Xóa node hỏng và join lại cùng tên (node ma xám trong GUI)](../cases/pve/ghost-node-rejoin.md)
- [Lỗi cfs-lock "got lock request timeout" (pmxcfs, HA, replication)](../cases/pve/cfs-lock-timeout.md)
- [Nâng cấp Proxmox VE 8 lên 9 trong cluster có Ceph](../cases/pve/pve-upgrade-8to9.md)
- [Một node chết hẳn (hỏng phần cứng): khôi phục dịch vụ](../cases/pve/node-dead-recovery.md)
- [Nâng cấp Ceph Quincy 17.2.8 → Reef 18.2.8 → Squid 19.2.4 trên PVE 8.4 (3 node, có CephFS)](../runbooks/rb-ceph-upgrade-quincy-reef-squid.md)
- [Bảo trì production: tắt HA và đặt cờ bảo trì Ceph trước khi tắt node](../runbooks/rb-prod-maintenance.md)
- [PVE host hỏng đĩa boot, không có backup cấu hình: kiểm kê và dựng lại node](../cases/pve/pve-host-rebuild-no-config-backup.md)
- [Proxmox ZFS replication: cấu hình và kiểm thử khôi phục VM](../runbooks/rb-pve-zfs-replication.md)
- [Xóa node Proxmox khỏi cluster an toàn (VM, HA và Ceph)](../runbooks/rb-pve-remove-node.md)
