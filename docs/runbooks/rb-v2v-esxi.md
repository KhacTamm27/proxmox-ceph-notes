# V2V VMware ESXi sang Proxmox bằng StarWind V2V Converter

[← Mục lục](../../README.md) · Runbook

**Mục tiêu:** Chuyển VM từ ESXi sang Proxmox bằng converter, kiểm thử trong môi trường cô lập và giữ nguyên nguồn để rollback.

**Điều kiện trước khi làm:** Xác minh tương thích của đúng phiên bản StarWind V2V với phiên bản PVE hiện tại trên tài liệu nhà cung cấp; không dựa vào ghi chú tương thích PVE 9.x đã cũ. Có backup, kiểm kê snapshot/disk/firmware và dung lượng ZFS đích đủ cho image cùng headroom vận hành.

## Các bước

1. Kiểm tra backup, disk/VMDK, snapshot và trạng thái VM nguồn; lên lịch quiesce/shutdown ứng dụng khi cần tính nhất quán

2. Trong StarWind V2V chọn ESXi làm nguồn, xác thực host và VM, rồi chọn node/storage Proxmox đích

3. Với đích ZFS, chọn định dạng Raw/ZVOL; không dùng qcow2 nếu backend không hỗ trợ. Xác nhận dung lượng trước khi bắt đầu

```bash
pvesm status
zpool list
```

4. Theo dõi converter log đến khi hoàn tất; đối chiếu số lượng disk và cấu hình firmware của VM mới

```bash
qm config <vmid>
```

5. Boot target trên network cô lập; với Windows dùng SATA tạm để boot nếu thiếu driver, cài VirtIO rồi mới chuyển SCSI/NIC. Giữ VM ESXi nguyên trạng đến khi cutover được duyệt

```bash
qm status <vmid>
```

## Lưu ý

Online conversion có thể tạo snapshot nhưng không đảm bảo nhất quán ứng dụng hoặc bắt kịp mọi ghi mới; chọn thời điểm cutover và shutdown nguồn theo yêu cầu dữ liệu. Không xóa snapshot ESXi theo phỏng đoán khi conversion lỗi; trước hết đọc log và xác minh backup/trạng thái chain. Tốc độ phụ thuộc converter, nguồn, mạng và storage đích; thông lượng 10Gb không bảo đảm converter dùng hết băng thông. Chỉ gỡ VMware Tools sau khi guest boot và quản trị ổn định trên PVE.

## Nguồn tham khảo

- [StarWind V2V Converter (tài liệu sản phẩm)](https://www.starwindsoftware.com/starwind-v2v-converter)
- [Proxmox VE qm manual](https://pve.proxmox.com/pve-docs/qm.1.html)

<!-- từ khóa: v2v vmware esxi vmfs vsan starwind converter proxmox pve vmdk zfs raw ovmf migration -->
