# local-lvm (thin pool) đầy

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** local-lvm gần 100%, VM bị I/O error hoặc treo, log có "thin pool ... out of space".

**Nguyên nhân hay gặp:** Data hoặc metadata của thin pool đầy do snapshot tích tụ, đĩa cấp phát vượt dung lượng thật (overprovision).

## Các bước xử lý

1. Xem mức đầy của data và metadata

```bash
pvesm status
lvs -a
```

2. Tìm snapshot và đĩa chiếm nhiều chỗ

```bash
lvs -o lv_name,lv_size,data_percent,metadata_percent
```

3. Giải phóng: xóa snapshot không cần (trong VM Linux chạy fstrim để trả block đã xóa)

```bash
qm delsnapshot <vmid> <snapname>
fstrim -av
```

4. Nếu VG còn trống thì mở rộng pool, nếu metadata đầy thì mở rộng metadata

```bash
lvextend -L +<size> <vg>/data
lvextend --poolmetadatasize +<size> <vg>/data
```

## Lưu ý

Pool đầy 100% có thể làm hỏng filesystem trong VM, nên đặt cảnh báo ở khoảng 80%. Cẩn thận khi overprovision.

<!-- từ khóa: proxmox lvm thin pool đầy local-lvm out of space metadata io error fstrim snapshot -->
