# P2V Windows: Disk2vhd, import VHDX và cài driver Proxmox

[← Mục lục](../../README.md) · Runbook

**Mục tiêu:** Chuyển một máy Windows vật lý sang VM Proxmox bằng VHD/VHDX, giữ máy nguồn và kiểm thử bản sao trước khi cutover.

**Điều kiện trước khi làm:** Backup máy nguồn và ứng dụng đã kiểm tra. Kiểm kê dung lượng, partition/volume hệ thống và dữ liệu; biết BIOS Legacy hay UEFI. Suspend/decrypt BitLocker theo chính sách và giữ recovery key ngoại tuyến an toàn. Có đủ dung lượng tạm cho image.

## Các bước

1. Trên Windows nguồn, dùng Disk2vhd từ Microsoft Sysinternals; chọn đủ các volume cần boot (bao gồm EFI/System Reserved và volume phục hồi cần thiết), xác nhận VSS thành công

2. Copy file VHD/VHDX sang node PVE và tạo VM với firmware khớp máy nguồn; UEFI cần cấu hình OVMF và EFI disk

```bash
qm create <vmid> --name <vm-name> --memory <MiB> --cores <count> --net0 e1000,bridge=<bridge>
```

3. Import disk vào storage đích; gắn disk import được vào SATA tạm thời để Windows boot bằng driver có sẵn

```bash
qm importdisk <vmid> <path-to-image.vhdx> <target-storage>
qm config <vmid>
```

4. Boot trong network cô lập, cài VirtIO drivers và QEMU Guest Agent; chỉ sau khi driver controller đã được cài và kiểm tra mới chuyển disk/NIC sang VirtIO

```bash
qm status <vmid>
```

5. Kiểm tra boot, dữ liệu, dịch vụ và network; chỉ cutover sau khi có phương án quay lại máy nguồn

## Lưu ý

Không đổi firmware Legacy/UEFI hoặc chuyển SATA sang VirtIO ngay trước lần boot đầu. Lỗi boot/BCD không có một chuỗi `bootrec` áp dụng cho mọi máy; trước tiên xác nhận đúng disk, EFI/System Reserved partition và firmware rồi dùng Windows Recovery phù hợp. VSS giúp tạo snapshot filesystem nhưng không bảo đảm nhất quán ứng dụng cho mọi database; quiesce dịch vụ hoặc dùng backup application-consistent khi cần. Không xóa/ghi đè máy nguồn sau khi export cho tới khi VM mới được nghiệm thu.

## Nguồn tham khảo

- [Microsoft Sysinternals Disk2vhd](https://learn.microsoft.com/en-us/sysinternals/downloads/disk2vhd)
- [Proxmox VE qm manual](https://pve.proxmox.com/pve-docs/qm.1.html)

<!-- từ khóa: p2v windows physical server pc disk2vhd vhdx vhd importdisk virtio driver sata uefi efi bcd chuyển máy vật lý -->
