# NAS NFS làm storage dùng chung cho cluster Proxmox

[← Mục lục](../../README.md) · Runbook

**Mục tiêu:** Cho 3 node Proxmox mount chung một thư mục xuất từ NFS server, chứa trực tiếp file .qcow2 hoặc .raw của VM. Dễ triển khai, phù hợp lab hoặc tải vừa phải.

**Điều kiện trước khi làm:** Một máy đóng vai NFS server, các node Proxmox truy cập được tới nó.

## Các bước

1. Trên NFS server: cài, tạo thư mục, khai báo export (thay <subnet> bằng dải mạng được phép), khởi động dịch vụ

```bash
apt update && apt install nfs-kernel-server -y
mkdir -p /mnt/pve-shared
chown nobody:nogroup /mnt/pve-shared
chmod 777 /mnt/pve-shared
echo "/mnt/pve-shared <subnet>(rw,sync,no_subtree_check,no_root_squash)" >> /etc/exports
exportfs -a
systemctl restart nfs-kernel-server
systemctl enable nfs-kernel-server
```

2. Trên các node Proxmox: kiểm tra kết nối tới export trước

```bash
apt install nfs-common -y
showmount -e <IP_NFS_SERVER>
```

3. Trên GUI: Datacenter, Storage, Add, NFS. Server = IP NFS server, Export = /mnt/pve-shared, Content = Disk image, ISO image, Container template, Nodes = All

4. Kiểm tra trên từng node

```bash
pvesm status
```

## Lưu ý

chmod 777 và no_root_squash trong ghi chú gốc tiện cho lab nhưng quá rộng cho production, nên giới hạn quyền thư mục và dải mạng. NFS treo thường làm pvestatd treo theo (xem case dấu hỏi unknown).

<!-- từ khóa: runbook nas nfs storage dùng chung exports nfs-kernel-server showmount mount share qcow2 -->
