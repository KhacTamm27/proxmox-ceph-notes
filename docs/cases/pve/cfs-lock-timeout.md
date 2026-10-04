# Lỗi cfs-lock "got lock request timeout" (pmxcfs, HA, replication)

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** Log có "cfs-lock ... error: got lock request timeout" (từ pvescheduler, pvestatd, ha-crm), tác vụ HA/replication/backup lỗi, GUI báo unknown.

**Nguyên nhân hay gặp:** Hệ thống file cụm (pmxcfs) không xin được khóa: thường là triệu chứng của cluster mất đồng bộ, corosync/mạng có vấn đề, hoặc pmxcfs trên một node bị treo.

## Các bước xử lý

1. Quorum và corosync có ổn không (đây là gốc phổ biến nhất)

```bash
pvecm status
corosync-cfgtool -s
```

2. Trạng thái và log của pve-cluster

```bash
systemctl status pve-cluster corosync
journalctl -u pve-cluster -u pvescheduler --since "1 hour ago"
```

3. Thử ghi vào /etc/pve để biết pmxcfs có phản hồi không

```bash
touch /etc/pve/.writetest
rm /etc/pve/.writetest
```

4. Nếu pmxcfs treo trên một node, restart dịch vụ cụm node đó (từng node một)

```bash
systemctl restart pve-cluster
```

## Lưu ý

Có người xóa thủ công thư mục khóa trong /etc/pve/priv/lock để hết lỗi nhưng chỉ tạm thời, lỗi tái phát vì nguyên nhân gốc (cluster hoặc mạng) vẫn còn. Chỉ xóa khóa khi hiểu rõ khóa nào và chắc không còn tiến trình nào đang giữ.

## Nguồn tham khảo

- [Proxmox forum: cfs lock domain-ha timeout](https://forum.proxmox.com/threads/cfs-lock-domain-ha-timeout-master-old-timestamp.48347/latest)
- [Proxmox forum: cluster 3 node status unknown, cfs-lock](https://forum.proxmox.com/threads/cluster-of-3-nodes-with-status-unknown-only-if-2-specific-nodes-are-online.164399/)

<!-- từ khóa: proxmox cfs-lock got lock request timeout pmxcfs pve-cluster /etc/pve ha replication pvescheduler authkey lỗi lock cluster -->
