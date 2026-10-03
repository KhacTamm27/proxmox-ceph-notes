# VM bị lock (backup/snapshot), không start hoặc migrate được

[← Mục lục](../../README.md)

**Triệu chứng:** Báo "VM is locked (backup)" hoặc "(snapshot)", không start, stop, migrate hoặc xóa được.

**Nguyên nhân hay gặp:** Tác vụ backup hoặc snapshot bị ngắt giữa chừng (mất mạng, node reboot, task bị kill) và để lại khóa.

## Các bước xử lý

1. Xem VM đang bị khóa kiểu gì

```bash
qm config <vmid>
```

2. Chắc chắn không còn backup hay restore đang chạy

```bash
ps aux | grep -E "vzdump|qmrestore"
pvesh get /nodes/<node>/tasks --limit 20
```

3. Mở khóa

```bash
qm unlock <vmid>
```

4. Kiểm tra lại trạng thái VM và đĩa trước khi start

```bash
qm status <vmid>
qm config <vmid>
```

## Lưu ý

Chỉ unlock khi chắc không còn tiến trình nào đang dùng VM. Với container dùng pct unlock <ctid>. Sau backup bị ngắt nên kiểm tra snapshot rác trên VM.

<!-- từ khóa: proxmox vm lock locked backup snapshot unlock qm không start migrate treo -->
