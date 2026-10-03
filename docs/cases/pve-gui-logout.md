# GUI Proxmox bị đăng xuất liên tục hoặc không đăng nhập được

[← Mục lục](../../README.md)

**Triệu chứng:** GUI bị đá ra sau một thời gian ngắn, báo "permission denied" hoặc "invalid ticket", trang tải chậm hoặc treo.

**Nguyên nhân hay gặp:** Giờ lệch giữa node và máy dùng trình duyệt (hoặc giữa các node) làm ticket không hợp lệ; pveproxy hoặc pvedaemon treo; cluster mất quorum.

## Các bước xử lý

1. So sánh giờ của node với giờ thực, và cả giờ máy đang dùng trình duyệt

```bash
timedatectl
chronyc tracking
```

2. Trạng thái các service giao diện và cluster

```bash
systemctl status pveproxy pvedaemon pve-cluster
pvecm status
```

3. Xem log pveproxy quanh thời điểm lỗi

```bash
journalctl -u pveproxy --since "1 hour ago"
```

4. Khởi động lại service giao diện (không ảnh hưởng VM đang chạy)

```bash
systemctl restart pveproxy pvedaemon
```

## Lưu ý

Thử trình duyệt ẩn danh hoặc xóa cookie PVEAuthCookie để loại trừ lỗi phía client. Nếu truy cập qua reverse proxy hoặc VIP thì kiểm tra thêm giờ và timeout trên lớp đó.

<!-- từ khóa: proxmox gui web logout đăng xuất session ticket pveproxy không đăng nhập lệch giờ -->
