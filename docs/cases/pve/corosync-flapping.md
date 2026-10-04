# Corosync link chập chờn, retransmit, node tự reboot (HA watchdog)

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** Log corosync có "Retransmit List", knet link down/up, "Token has not been received"; cluster mất quorum rồi phục hồi; các node có HA tự reboot cùng lúc.

**Nguyên nhân hay gặp:** Mạng corosync bị trễ hoặc rớt gói: dùng chung đường với lưu lượng Ceph/backup/replication, đặt link corosync trên bond (failover của bond cộng với phục hồi link của corosync), MTU lệch hoặc switch lỗi.

## Các bước xử lý

1. Xem log corosync quanh thời điểm lỗi

```bash
journalctl -u corosync --since "1 hour ago"
```

2. Trạng thái link hiện tại và quorum

```bash
corosync-cfgtool -s
pvecm status
```

3. Xác nhận corosync thật sự đang đi qua đường mạng riêng đã dự định, và đường đó thông MTU

```bash
cat /etc/pve/corosync.conf
ping -M do -s 1472 <node-ip>
```

4. Kiểm tra lỗi NIC và cổng switch

```bash
ip -s link show <if>
ethtool -S <if>
```

## Lưu ý

Hướng dẫn từ cộng đồng và nhân viên Proxmox: dùng NIC vật lý riêng cho corosync (1G đủ vì độ trễ mới là yếu tố quan trọng), thêm link thứ hai (link1) để dự phòng thay vì dùng bond cho corosync, và không để Ceph, backup, replication chiếm đường corosync. Sửa corosync.conf cần theo đúng quy trình trong tài liệu Cluster Manager (sửa bản .new và tăng config_version). Node có HA reboot khi mất quorum là hành vi thiết kế của watchdog.

## Nguồn tham khảo

- [Proxmox forum: Retransmit list, cả HA cluster reboot](https://forum.proxmox.com/threads/totem-retransmit-list-causing-entire-ha-cluster-to-reboot-unexpectedly.167112/)
- [Proxmox forum: Nodes constantly fencing](https://forum.proxmox.com/goto/post?id=776001)

<!-- từ khóa: proxmox corosync flapping retransmit knet link down token cluster reboot watchdog fence mất quorum bond lacp mạng cluster riêng -->
