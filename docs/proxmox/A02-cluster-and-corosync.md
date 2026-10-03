# A2 · Cluster and corosync

[← Mục lục](../../README.md) · Proxmox host · 16 lệnh

[← A1 System and node](../proxmox/A01-system-and-node.md) · [A3 Virtual machines (qm) →](../proxmox/A03-virtual-machines-qm.md)

## Status

```bash
# Xem quorum, số phiếu và link của cluster Proxmox | Quorum, votes, links
# từ khóa: quorum mất quorum no quorum cluster vote
pvecm status

# Liệt kê các node trong cluster | Cluster members
# từ khóa: node thành viên danh sách
pvecm nodes

# Chi tiết quorum theo corosync | Quorum details
# từ khóa: quorum votes
corosync-quorumtool -s
```

## Links

```bash
# Trạng thái từng link knet giữa các node, phát hiện link đứt | KNET link status per node
# từ khóa: link down mạng cluster knet đứt
corosync-cfgtool -s

# Danh sách node và link corosync | Node and link list
# từ khóa: node link
corosync-cfgtool -n

# Thành viên corosync đang chạy thực tế | Runtime member info
# từ khóa: members runtime
corosync-cmapctl runtime.members
```

## Logs

```bash
# Theo dõi log corosync theo thời gian thực | Follow corosync log
# từ khóa: log corosync retransmit token lost link
journalctl -u corosync -f

# Theo dõi log pmxcfs (thư mục /etc/pve) | Follow pmxcfs log
# từ khóa: log pmxcfs etc/pve read-only
journalctl -u pve-cluster -f
```

## Config

```bash
# Xem cấu hình corosync của cluster | Cluster config
# từ khóa: config corosync
cat /etc/pve/corosync.conf
```

## Membership

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

## Recovery

```bash
# Chạy pmxcfs chế độ local khi không có quorum (biện pháp cuối) | Start pmxcfs in local mode without quorum (emergency)
# từ khóa: không quorum sửa etc/pve local mode
pmxcfs -l

# Khởi động lại stack cluster khi treo hoặc lệch trạng thái | Restart cluster stack
# từ khóa: restart cluster corosync treo
systemctl restart pve-cluster corosync
```
