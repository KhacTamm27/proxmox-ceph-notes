# Console VM qua proxy không kết nối (màn hình đen, 401, 403, 404, 502, WebSocket đứt)

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** Bấm Remote Console trên portal chỉ thấy màn hình đen, báo không kết nối, hoặc F12 > Network thấy vncproxy hoặc vncwebsocket lỗi (401, 403, 404, 502, không lên 101).

**Nguyên nhân hay gặp:** Ticket hết hạn hoặc sai realm, user portal thiếu quyền console, tiền tố vmid/node không khớp server block, Nginx không tới được node cổng 8006, thiếu header WebSocket, hoặc chứng chỉ SSL hết hạn.

## Các bước xử lý

1. Xem lỗi đầu tiên ở trình duyệt: F12 > Network, lọc vnc, ghi lại mã lỗi của vncproxy và vncwebsocket

2. Phía proxy: log lỗi và cú pháp cấu hình

```bash
tail -f /var/log/nginx/proxy-error.log
nginx -t
```

3. Proxy có tới được node không (mã 200 hoặc 401 đều là có tới)

```bash
curl -sk -o /dev/null -w "%{http_code}\n" https://<node-ip>:8006/
```

4. VM có đang chạy và user portal có quyền không

```bash
qm status <vmid>
pveum acl list
```

5. Chứng chỉ SSL còn hạn không

```bash
openssl x509 -enddate -noout -in /etc/nginx/<domain>.crt
```

## Lưu ý

Các bước kiểm tra chi tiết từng chặng (lấy ticket, đặt cookie, URL chuẩn, đọc F12) nằm trong runbook gỡ lỗi console. Cấu hình proxy chuẩn nằm trong runbook Nginx proxy console.

<!-- từ khóa: console proxy nginx novnc không kết nối màn hình đen 401 403 404 502 websocket vncwebsocket 101 ticket pveauthcookie portal remote console lỗi -->
