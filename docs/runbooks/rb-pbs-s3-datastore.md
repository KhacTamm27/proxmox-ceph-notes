# PBS: tạo Datastore S3 với local cache ZFS và backup từ PVE

[← Mục lục](../../README.md) · Runbook

**Mục tiêu:** Dùng một bucket S3 (nhà cung cấp S3-compatible) làm datastore của PBS 4.x, có vùng đệm local cache trên ZFS, rồi thêm vào PVE và backup thử.

**Điều kiện trước khi làm:** PBS 4.x đã cài. Có thông tin xác thực S3 được lưu an toàn (không đưa key vào command/log/tài liệu). Có một SSD hoặc mảng ZFS làm cache. Datastore S3 hiện là tech preview.

## Các bước

1. Tạo cache ZFS với điểm mount riêng, không lồng trong datastore local khác (tránh lỗi nested datastore), cấp quyền cho user backup

```bash
zfs create -o mountpoint=/s3-cache <pool>/s3-cache
chown backup:backup /s3-cache
chmod 700 /s3-cache
```

2. Trên PBS Web GUI: Configuration, S3 Endpoints, Add. Điền ID, Endpoint (<s3-endpoint>), Access Key và Secret Key an toàn; chọn Path Style theo yêu cầu của nhà cung cấp (một số S3-compatible endpoint bắt buộc bật), nhập Fingerprint nếu được yêu cầu

3. Datastore, Add Datastore: Name, Type = S3 (tech preview), Local Cache = /s3-cache, S3 Endpoint ID, Bucket = <bucket>. Với bucket mới, để Overwrite in-use marker tắt. Chỉ bật khi nhận lại bucket cũ theo runbook khôi phục PBS và đã tắt hẳn PBS cũ.

4. Trên PVE: Datacenter, Storage, Add, Proxmox Backup Server, rồi backup thử một VM

```bash
vzdump <vmid> --storage <pbs-storage> --mode snapshot
```

5. Kết quả mong đợi: thấy thư mục vm/<vmid> ở phần Content của datastore S3

## Lưu ý

Dung lượng trên S3 phụ thuộc dữ liệu thực tế, deduplication, nén và vùng trống; không lấy một ví dụ dung lượng làm cam kết. Nếu bật Encryption thì phải lưu file key mã hóa (.json) hoặc mật khẩu ở nơi an toàn: mất key là mất dữ liệu vĩnh viễn dù S3 còn nguyên. Thư mục cache phải thuộc user backup; chỉ khi đường dẫn cache đã được kiểm tra đúng mới cân nhắc chown -R backup:backup <đường dẫn cache>. Không ghi Access Key, Secret Key, endpoint riêng tư hoặc fingerprint của môi trường thật vào tài liệu công khai. Nhận lại bucket cũ xem [case phục hồi PBS S3](../cases/pve/pbs-s3-recovery.md).

<!-- từ khóa: runbook pbs proxmox backup server s3 datastore local cache zfs endpoint path style bucket backup dedup restore adopt migration longvan long vân -->
