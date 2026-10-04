# Xóa node hỏng và join lại cùng tên (node ma xám trong GUI)

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** Đã pvecm delnode nhưng node vẫn hiện xám trong GUI; cài lại node cùng tên không join được hoặc báo lỗi SSH/chứng chỉ.

**Nguyên nhân hay gặp:** Cluster giữ lại thư mục cấu hình của node đã xóa trong /etc/pve/nodes; chứng chỉ và khóa SSH cũ trùng tên.

## Các bước xử lý

1. Xác nhận node đã thật sự bị gỡ khỏi cluster (và máy cũ đã tắt hẳn)

```bash
pvecm status
pvecm nodes
```

2. Nếu chưa gỡ, chạy từ một node còn sống

```bash
pvecm delnode <node>
```

3. Xem thư mục còn sót của node, rồi xóa ĐÚNG thư mục của node đã gỡ (xóa nhầm tên là hỏng cluster)

```bash
ls /etc/pve/nodes
rm -rf /etc/pve/nodes/<OLD-NODE-NAME>
```

4. Cài lại node mới sạch hoàn toàn rồi join, sau đó cập nhật chứng chỉ vì dùng lại tên cũ

```bash
pvecm add <existing-node-ip>
pvecm updatecerts
```

5. Nếu cụm có Ceph, kiểm tra cấu hình còn nhắc IP của node cũ không

```bash
cat /etc/pve/ceph.conf
```

## Lưu ý

Node đã gỡ không được bật lại với cấu hình cũ. Chỉ nên join lại cùng tên khi node đã được cài lại từ đầu hoặc là máy hoàn toàn mới. Nếu node đó có MON hoặc OSD Ceph thì gỡ chúng khỏi Ceph đúng cách trước khi xóa node.

## Nguồn tham khảo

- [Proxmox forum: Older node was re-installed and wants to join](https://forum.proxmox.com/goto/post?id=427504)
- [Proxmox forum: Remove node from cluster](https://forum.proxmox.com/goto/post?id=640499)

<!-- từ khóa: proxmox xóa node delnode node ma xám gui join lại cùng tên hostname reinstall updatecerts /etc/pve/nodes known_hosts -->
