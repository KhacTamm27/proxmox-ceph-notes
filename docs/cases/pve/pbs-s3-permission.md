# PBS S3: ENOENT hoặc Permission denied với cache, không thấy backup

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** Tạo hoặc mount datastore S3 báo ENOENT hoặc Permission denied, backup lỗi, hoặc PBS mới không thấy bản backup cũ.

**Nguyên nhân hay gặp:** Thư mục cache không thuộc user backup, cache lồng trong datastore local, hoặc chưa bật Overwrite in-use marker khi nhận lại bucket cũ.

## Các bước xử lý

1. Kiểm tra chủ sở hữu, quyền và dataset của thư mục cache

```bash
ls -ld /s3-cache
zfs list
```

2. Cấp lại quyền cho user backup

```bash
chown -R backup:backup /s3-cache
chmod 700 /s3-cache
```

3. Xem log dịch vụ PBS quanh thời điểm lỗi

```bash
journalctl -u proxmox-backup-proxy --since "30 min ago"
```

## Lưu ý

Cache phải là điểm mount riêng, không nằm trong datastore local khác. Nhận lại bucket cũ mà không thấy backup thì kiểm tra đã tick Overwrite in-use marker (chỉ khi PBS cũ đã tắt hẳn). Xem runbook PBS S3.

<!-- từ khóa: pbs s3 enoent permission denied cache chown backup datastore nested không thấy backup overwrite in-use marker -->
