# Proxmox boot ZFS mirror: kiểm tra trước khi thay disk rpool

[← Mục lục](../../README.md) · Runbook

**Mục tiêu:** Thu thập thông tin và chuẩn bị an toàn cho việc thay disk trong rpool mirror của Proxmox VE.

**Điều kiện trước khi làm:** Cần xác định node, PVE version, trạng thái rpool, boot mode (UEFI/Legacy), bootloader (proxmox-boot-tool/GRUB), partition layout và chính xác disk cũ/mới. Tài liệu PDF nguồn chỉ có phần giới thiệu và ảnh không trích được lệnh thay thế; vì vậy runbook này cố ý dừng trước các lệnh ghi/xóa.

## Các bước

1. Ghi lại phiên bản và tình trạng rpool, gồm đường dẫn thiết bị đầy đủ

```bash
pveversion -v
zpool status -P -v rpool
```

2. Đối chiếu tên, dung lượng, serial/WWN, phân vùng và filesystem của tất cả ổ; xác nhận ổ mới không chứa dữ liệu cần giữ

```bash
lsblk -o NAME,SIZE,SERIAL,WWN,PARTUUID,FSTYPE,MOUNTPOINTS
```

3. Nếu hệ thống dùng proxmox-boot-tool, ghi nhận trạng thái EFI; nếu không nhận diện rõ bootloader hoặc mirror đang degraded nặng, dừng và chuyển sang quy trình chính thức phù hợp

```bash
proxmox-boot-tool status
```

4. Chỉ sau khi xác định đúng layout và đã có backup: thực hiện quy trình replace theo tài liệu PVE hiện hành cho đúng boot mode, rồi theo dõi resilver và thử boot từ disk thay thế trong cửa sổ bảo trì

```bash
zpool status -P -v rpool
```

## Lưu ý

Không chạy `zpool replace`, `sgdisk`, `wipefs`, `proxmox-boot-tool format/init` hoặc `grub-install` theo một lệnh mẫu chung khi chưa đối chiếu phân vùng, sector/WWN và boot mode; chọn nhầm disk có thể phá hủy rpool hoặc làm node không boot. Sau replace phải xác minh cả resilver lẫn khả năng boot độc lập từ ổ còn lại. Do PDF gốc không có các bước thay ổ dạng văn bản, không suy diễn một chuỗi lệnh destructive từ ảnh thiếu.

## Nguồn tham khảo

- [Proxmox VE Admin Guide](https://pve.proxmox.com/pve-docs/pve-admin-guide.html)
- [OpenZFS zpool-replace manual](https://openzfs.github.io/openzfs-docs/man/master/8/zpool-replace.8.html)

<!-- từ khóa: zfs rpool root boot disk mirror thay disk lỗi replace bootloader efi grub proxmox-boot-tool disk boot zpool replace -->
