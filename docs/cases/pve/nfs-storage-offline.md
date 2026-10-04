# Storage NFS offline hoặc không thêm được vào Proxmox

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** Storage NFS hiện dấu hỏi hoặc offline, không thêm được vào Datacenter > Storage, lệnh pvesm status chậm hoặc treo.

**Nguyên nhân hay gặp:** Node thiếu nfs-common, export không cho phép subnet của node, tường lửa chặn, hoặc NFS server đã dừng.

## Các bước xử lý

1. Từ node: server có export gì

```bash
apt install nfs-common -y
showmount -e <IP_NFS_SERVER>
```

2. Trên NFS server: dịch vụ và danh sách export hiện hành

```bash
systemctl status nfs-kernel-server
exportfs -v
```

3. Thử mount tay để thấy lỗi rõ

```bash
mkdir -p /mnt/nfstest
mount -t nfs <IP_NFS_SERVER>:/mnt/pve-shared /mnt/nfstest
```

4. Xem trạng thái storage (dùng timeout để lệnh không bị kẹt)

```bash
timeout 20 pvesm status
```

## Lưu ý

Storage NFS treo có thể kéo theo pvestatd treo làm node hiện dấu hỏi (xem case dấu hỏi). Nhớ umount thư mục thử sau khi kiểm tra.

<!-- từ khóa: nfs storage offline không mount showmount exportfs nfs-common firewall proxmox không thêm được nas -->
