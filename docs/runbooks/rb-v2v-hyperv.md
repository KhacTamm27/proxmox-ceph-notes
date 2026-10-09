# V2V Hyper-V sang Proxmox bằng StarWind V2V Converter

[← Mục lục](../../README.md) · Runbook

**Mục tiêu:** Chuyển VM từ Hyper-V sang Proxmox, giữ nguyên bản nguồn và kiểm thử VM đích trước khi chuyển dịch vụ.

**Điều kiện trước khi làm:** Xác nhận phiên bản StarWind V2V và PVE tương thích; có backup độc lập, dung lượng đích và cửa sổ cutover. Kiểm kê Generation 1/2, BIOS/UEFI, disk/checkpoint và ứng dụng. Dùng credential an toàn, không ghi password/token vào tài liệu hoặc log.

## Các bước

1. Kiểm tra backup và checkpoint của VM nguồn; thống nhất với chủ ứng dụng cách quiesce/shutdown để có bản chuyển đổi nhất quán

2. Trong StarWind V2V chọn Hyper-V làm nguồn, xác thực host, chọn đúng VM và chọn Proxmox VE làm đích

3. Đặt VMID/name/storage đích và định dạng được storage hỗ trợ; với ZFS chọn Raw/ZVOL, không ép qcow2

```bash
pvesm status
```

4. Convert, đọc log tới trạng thái hoàn tất rồi cấu hình firmware tương ứng; VM Generation 2 thường cần OVMF và EFI disk

5. Boot target trên network cô lập, cài VirtIO drivers/Guest Agent và kiểm tra ứng dụng; chỉ cutover sau khi tắt VM nguồn để tránh hai bản cùng chạy

```bash
qm config <vmid>
qm status <vmid>
```

## Lưu ý

Không giả định conversion trực tiếp khi VM đang bật là application-consistent hoặc không có data loss. Giữ Hyper-V VM và checkpoint/source disk đến khi nghiệm thu. Nếu cần đổi Windows từ controller SATA sang SCSI/VirtIO, cài và kiểm tra driver trước, rồi đổi trong maintenance window. Không xóa checkpoint/snapshot nguồn hoặc gỡ Hyper-V VM như bước xử lý lỗi mặc định; đánh giá backup và trạng thái merge trước.

## Nguồn tham khảo

- [Proxmox VE qm manual](https://pve.proxmox.com/pve-docs/qm.1.html)

<!-- từ khóa: v2v hyper-v hyperv microsoft starwind converter proxmox pve vhdx gen2 uefi ovmf virtio migrate vm -->
