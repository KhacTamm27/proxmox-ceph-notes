# Backup vzdump lỗi hoặc treo

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** Job backup báo lỗi, chạy rất lâu, hoặc để lại VM bị lock.

**Nguyên nhân hay gặp:** Storage backup đầy hoặc mất kết nối, guest agent không phản hồi khi freeze, VM bị lock, hai job chồng nhau.

## Các bước xử lý

1. Storage đích còn chỗ và đang online không

```bash
pvesm status
df -h
```

2. Có tiến trình backup nào đang chạy hoặc treo

```bash
ps aux | grep vzdump
```

3. Guest agent của VM có phản hồi không

```bash
qm agent <vmid> ping
```

4. Nếu VM bị lock sau backup lỗi, mở khóa (chắc chắn không còn vzdump chạy)

```bash
qm unlock <vmid>
```

5. Chạy thử thủ công một VM để thấy lỗi rõ

```bash
vzdump <vmid> --storage <storage> --mode snapshot --compress zstd
```

## Lưu ý

Lỗi freeze thường do guest agent trong VM không chạy, cài hoặc bật qemu-guest-agent. Nên giãn lịch để các job backup không chồng nhau.

<!-- từ khóa: proxmox backup vzdump lỗi treo guest agent freeze storage đầy pbs lock -->
