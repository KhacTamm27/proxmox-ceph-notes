# Storage dùng chung giữa hai cluster Proxmox gây xung đột lock/VMID

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** VM start/migrate hoặc thao tác storage thất bại bất thường; cùng một NFS export, LUN hoặc Ceph pool đang được cấu hình cho hai cluster Proxmox độc lập; VMID có thể trùng.

**Nguyên nhân hay gặp:** Storage locking của Proxmox chỉ phối hợp trong phạm vi một cluster, không hoạt động xuyên ranh giới hai cluster. Hai cluster cùng truy cập storage có thể đồng thời thao tác lên cùng dữ liệu và phát sinh xung đột VMID.

## Các bước xử lý

1. Xác định cluster hiện tại và cấu hình storage trên node nghi vấn

```bash
pvecm status
cat /etc/pve/storage.cfg
pvesm status
```

2. Đối chiếu chính xác backend đang dùng: NFS export, LUN/target hoặc Ceph pool; kiểm tra cluster còn lại có cùng backend không

```bash
pvesm list <storage-id>
ceph fsid
ceph osd pool ls
```

3. Ngừng cấp quyền truy cập đồng thời; chọn cluster sở hữu storage và cô lập cluster còn lại trước khi tiếp tục ghi

4. Tạo storage riêng cho cluster cần tách, chuyển VM và dữ liệu sang storage đó rồi xác minh bản chuyển

```bash
pvesm status
qm config <vmid>
```

5. Chỉ sau khi đã chuyển dữ liệu và xác nhận không còn VM/client dùng backend cũ, gỡ cấu hình storage khỏi cluster không sở hữu nó

```bash
pvesm remove <storage-id>
pvesm status
```

## Lưu ý

Không cho hai cluster ghi đồng thời lên cùng một datastore, Ceph pool hoặc LUN; không xóa hay format backend trong lúc còn VM/client sử dụng. Việc gỡ một node khỏi cluster không tự thu hồi quyền truy cập shared storage. Nếu đang tách node khỏi cluster, làm theo đúng quy trình Cluster Manager chính thức và bảo đảm storage đã được tách trước khi join sang cluster khác.

## Nguồn tham khảo

- [Proxmox VE: Cluster Manager — separating a node](https://pve.proxmox.com/pve-docs/chapter-pvecm.html)

<!-- từ khóa: proxmox pve storage dùng chung hai cluster two clusters multiple cluster cluster boundary lock vmid conflict shared shared storage nfs ceph pool lun tách node -->
