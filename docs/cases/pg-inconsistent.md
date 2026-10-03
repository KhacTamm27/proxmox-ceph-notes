# PG inconsistent / scrub errors

[← Mục lục](../../README.md)

**Triệu chứng:** HEALTH_ERR, "pg x.y is active+clean+inconsistent", "N scrub errors".

**Nguyên nhân hay gặp:** Một bản sao của object khác các bản còn lại (bad sector, lỗi đĩa, lỗi bộ nhớ) bị deep-scrub phát hiện.

## Các bước xử lý

1. Lấy ID PG bị lỗi

```bash
ceph health detail
```

2. Xem object nào và bản sao nằm trên OSD nào bị lỗi

```bash
rados list-inconsistent-obj <pgid> --format=json-pretty
ceph pg map <pgid>
```

3. Kiểm tra sức khỏe đĩa của OSD chứa bản lỗi

```bash
smartctl -a /dev/<dev>
journalctl -u ceph-osd@<osd-id> --since "1 hour ago"
```

4. Sửa PG rồi theo dõi cho đến khi hết cảnh báo

```bash
ceph pg repair <pgid>
ceph -w
```

## Lưu ý

Xác định bản lỗi trước khi repair. Nếu cùng một OSD báo lỗi lặp lại thì đĩa đang hỏng, nên thay đĩa thay vì repair liên tục.

<!-- từ khóa: ceph pg inconsistent scrub error hỏng dữ liệu repair -->
