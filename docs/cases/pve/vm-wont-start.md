# VM không start được

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** qm start báo lỗi, task lỗi, VM dừng ngay sau khi bật.

**Nguyên nhân hay gặp:** Cluster mất quorum, storage chứa đĩa không available, thiếu RAM trên node, VM bị lock, file cấu hình trỏ tới đĩa hoặc thiết bị không tồn tại.

## Các bước xử lý

1. Chạy start để đọc thông báo lỗi chính xác

```bash
qm start <vmid>
```

2. Kiểm tra lock và đường dẫn đĩa trong cấu hình

```bash
qm config <vmid>
```

3. Storage và quorum có ổn không

```bash
pvesm status
pvecm status
```

4. Còn RAM trống không, và xem lệnh QEMU sẽ chạy

```bash
free -h
qm showcmd <vmid> --pretty
```

5. Xem log dịch vụ

```bash
journalctl -u pvedaemon --since "10 min ago"
```

## Lưu ý

Thấy "no quorum" thì xử lý theo case mất quorum trước. Thấy lock thì xem case VM bị lock.

<!-- từ khóa: proxmox vm không start khởi động lỗi timeout quota storage không đủ ram qm start -->
