# PBS: tạo Datastore S3 với local cache ZFS và backup từ PVE

[← Mục lục](../../README.md) · Runbook

**Mục tiêu:** Dùng một bucket S3 (nhà cung cấp S3-compatible) làm datastore của PBS 4.x, có vùng đệm local cache trên ZFS, rồi thêm vào PVE và backup thử.

**Điều kiện trước khi làm:** PBS 4.x đã cài. Có Access Key và Secret Key của nhà cung cấp S3. Có một SSD hoặc mảng ZFS làm cache. Datastore S3 hiện ghi là tech preview.

## Các bước

1. Tạo cache ZFS với điểm mount riêng, không lồng trong datastore local khác (tránh lỗi nested datastore), cấp quyền cho user backup

```bash
zfs create -o mountpoint=/s3-cache <pool>/s3-cache
chown backup:backup /s3-cache
chmod 700 /s3-cache
```

2. Trên PBS Web GUI: Configuration, S3 Endpoints, Add. Điền ID, Endpoint (<s3-endpoint>), Access Key, Secret Key, tích Path Style (bắt buộc), Fingerprint (<fingerprint>)

3. Datastore, Add Datastore: Name, Type = S3 (tech preview), Local Cache = /s3-cache, S3 Endpoint ID, Bucket = <bucket>. Mục Advanced tích Overwrite in-use marker (cho phép datastore này giành quyền kiểm soát bucket đang bị đánh dấu in-use, xem runbook khôi phục khi PBS hỏng)

4. Trên PVE: Datacenter, Storage, Add, Proxmox Backup Server, rồi backup thử một VM

```bash
vzdump <vmid> --storage <pbs-storage> --mode snapshot
```

5. Kết quả mong đợi: thấy thư mục vm/<vmid> ở phần Content của datastore S3

## Lưu ý

Dung lượng trên S3 thường nhỏ hơn nhiều so với đĩa VM (ví dụ VM đĩa 50GB chỉ khoảng 2.4GB) nhờ deduplication, nén, và bỏ qua vùng trống. Nếu bật Encryption thì phải lưu file key mã hóa (.json) hoặc mật khẩu ở nơi an toàn: mất key là mất dữ liệu vĩnh viễn dù S3 còn nguyên. Thư mục cache phải thuộc user backup, nếu gặp ENOENT hoặc Permission denied thì chạy chown -R backup:backup <đường dẫn cache>.

<!-- từ khóa: runbook pbs proxmox backup server s3 datastore local cache zfs endpoint path style bucket backup dedup -->
