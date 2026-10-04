# PBS hỏng hoặc tắt: dựng PBS mới nhận lại Datastore S3 (adopt) và restore

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** Máy PBS cũ lỗi phần cứng, cháy, hoặc chủ động tắt, cần khôi phục dữ liệu backup đang nằm trên bucket S3.

**Nguyên nhân hay gặp:** Dữ liệu backup nằm trên S3 nên còn nguyên, chỉ mất lớp quản lý và local cache của PBS cũ. PBS mới cần nhận lại (adopt) bucket đó.

## Các bước xử lý

1. Tắt hẳn PBS cũ trước. Trên PBS mới: tạo lại vùng cache trống (ZFS hoặc SSD đều được) và cấp quyền

```bash
zfs create -o mountpoint=/s3-recovery-cache <pool>/s3-recovery-cache
chown backup:backup /s3-recovery-cache
chmod 700 /s3-recovery-cache
```

2. Tạo lại S3 Endpoint y hệt cũ (cùng Endpoint, Access/Secret Key, Fingerprint, tích Path Style)

3. Add Datastore: đặt lại cùng Name với datastore cũ, Local Cache = /s3-recovery-cache, chọn S3 Endpoint vừa tạo, Bucket = đúng tên bucket cũ. Advanced bắt buộc tích Overwrite in-use marker để PBS mới giành quyền kiểm soát bucket khỏi PBS cũ

4. Vào Datastore, Content: danh sách backup sẽ hiện ra sau vài giây khi PBS tải metadata từ S3 về cache

5. Trên PVE: xóa liên kết tới PBS cũ, thêm PBS mới, chọn VM, Backup, chọn bản backup, Restore, rồi kiểm tra dữ liệu trong VM

```bash
qmrestore <backup-volume> <vmid>
```

## Lưu ý

Nếu PBS cũ có bật Encryption thì phải có file encryption key (.json) hoặc mật khẩu, mất key là mất dữ liệu vĩnh viễn dù S3 còn. Gặp ENOENT hoặc Permission denied thì chạy chown -R backup:backup <thư mục cache>. Chỉ tích Overwrite in-use marker khi chắc PBS cũ đã tắt hẳn.

<!-- từ khóa: proxmox pbs backup server hỏng cháy tắt dựng lại s3 datastore adopt overwrite in-use marker restore vm cache mã hóa key encryption -->
