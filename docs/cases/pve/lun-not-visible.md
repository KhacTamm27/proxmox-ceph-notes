# LUN iSCSI mới hoặc Volume Group không hiện trên một số node (Shared LVM)

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** Sau khi thêm LUN hoặc mở rộng VG, một số node không thấy thiết bị hoặc không thấy VG, pvesm status báo storage lỗi.

**Nguyên nhân hay gặp:** Node chưa rescan iSCSI, session iSCSI bị rớt, hoặc cache LVM trên node đó chưa được làm tươi.

## Các bước xử lý

1. Kiểm tra session iSCSI còn không, rescan để nhận LUN mới

```bash
iscsiadm -m session
iscsiadm -m session --rescan
lsblk
```

2. Làm tươi cache LVM trên node bị thiếu

```bash
pvscan --cache
vgscan
vgs
```

3. Kiểm tra storage từ phía Proxmox

```bash
pvesm status
```

## Lưu ý

Chỉ chạy pvcreate và vgextend trên một node, các node còn lại chỉ cần rescan và làm tươi cache. Session rớt liên tục thì kiểm tra mạng iSCSI và cân nhắc multipath. Xem runbook SAN iSCSI + Shared LVM.

<!-- từ khóa: iscsi lun không thấy vg shared lvm rescan pvscan vgscan session rớt san proxmox node không nhận mở rộng -->
