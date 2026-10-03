# MON down, ceph -s treo hoặc mất quorum Ceph

[← Mục lục](../../README.md)

**Triệu chứng:** ceph -s đứng treo hoặc báo "1/3 mons down", "mon.X is down".

**Nguyên nhân hay gặp:** Daemon MON dừng, ổ chứa /var/lib/ceph đầy (MON store phình), lệch giờ, mạng giữa các MON.

## Các bước xử lý

1. Xem MON nào còn trong quorum (nếu ceph -s còn trả lời)

```bash
ceph quorum_status -f json-pretty
```

2. Trên host MON: ceph -s treo thì hỏi thẳng qua admin socket

```bash
ceph daemon mon.<id> mon_status
```

3. Kiểm tra service, log và dung lượng ổ

```bash
systemctl status ceph-mon@<id>
journalctl -u ceph-mon@<id> --since "1 hour ago"
df -h /var/lib/ceph
```

4. Nếu store phình to thì compact, sau đó khởi động lại

```bash
ceph tell mon.<id> compact
systemctl restart ceph-mon@<id>
```

## Lưu ý

Cần đa số MON (2/3 hoặc 3/5) mới có quorum. Tuyệt đối không xóa thư mục store của MON khi chưa chắc còn đủ MON khác khỏe.

<!-- từ khóa: ceph mon down quorum mất quorum ceph -s treo monitor đầy disk -->
