# Xem lại Access Key và Secret Key của user S3

[← Mục lục](../../../README.md) · Case study Ceph

**Triệu chứng:** Cần tra lại Access Key/Secret Key để cấu hình client S3 hoặc kiểm tra lỗi xác thực.

**Nguyên nhân hay gặp:** Thông tin key không còn trong cấu hình ứng dụng, cần xác nhận key đang gắn với user RGW nào.

## Các bước xử lý

1. Xác định đúng UID của user S3

```bash
radosgw-admin user list
```

2. Xem key và trạng thái user; đối chiếu access_key với cấu hình client

```bash
radosgw-admin user info --uid=<uid>
```

3. Nếu cần key mới, tạo key rồi cập nhật client trước khi xóa key cũ

```bash
radosgw-admin key create --uid=<uid> --key-type=s3 --gen-access-key --gen-secret
```

4. Sau khi tất cả client đã chuyển sang key mới, mới thu hồi key cũ nếu không còn dùng

```bash
radosgw-admin key rm --uid=<uid> --access-key=<old-access-key>
```

## Lưu ý

Output user info có thể chứa Secret Key dạng rõ. Chỉ người được phân quyền mới xem; không dán output vào ticket/chat, ảnh chụp, log hoặc lịch sử chia sẻ. Nếu user info không còn Secret Key cần dùng thì tạo key mới và cập nhật client; không xóa key cũ cho đến khi xác nhận không còn dịch vụ nào dùng nó. Xóa key sẽ làm các client dùng key đó mất quyền truy cập.

## Nguồn tham khảo

- [Ceph docs: radosgw-admin](https://docs.ceph.com/en/reef/man/8/radosgw-admin/)

<!-- từ khóa: ceph rgw s3 xem lại access key secret key credentials thông tin đăng nhập user mất key -->
