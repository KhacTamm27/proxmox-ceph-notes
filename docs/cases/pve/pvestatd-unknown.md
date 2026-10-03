# Node hoặc VM hiện dấu hỏi (unknown), GUI không cập nhật

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** Trong GUI node, VM hoặc storage hiện dấu (?) xám, số liệu không cập nhật dù VM vẫn chạy.

**Nguyên nhân hay gặp:** pvestatd bị treo, thường vì một storage từ xa (NFS, CIFS, PBS) không phản hồi.

## Các bước xử lý

1. Xem trạng thái pvestatd

```bash
systemctl status pvestatd
journalctl -u pvestatd --since "30 min ago"
```

2. Tìm storage đang treo (dùng timeout để lệnh không bị kẹt)

```bash
timeout 20 pvesm status
```

3. Restart pvestatd (không ảnh hưởng VM đang chạy)

```bash
systemctl restart pvestatd
```

## Lưu ý

Nếu pvesm status hoặc df bị treo thì storage từ xa đang lỗi, xử lý mount hoặc mạng tới storage đó mới là gốc. Restart pvestatd chỉ là tạm thời.

<!-- từ khóa: proxmox unknown dấu hỏi pvestatd gui không cập nhật storage nfs treo node xám -->
