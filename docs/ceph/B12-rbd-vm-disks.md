# B12 · RBD (đĩa VM)

[← Mục lục](../../README.md) · Ceph · 26 lệnh · tên gốc: RBD (VM disks)

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← B11 Recovery, scrub và tinh chỉnh cấu hình](../ceph/B11-recovery-scrub-and-config-tuning.md) · [B13 RGW và S3 (radosgw-admin) →](../ceph/B13-rgw-and-s3-radosgw-admin.md)

## Liệt kê (List)

```bash
# [chỉ đọc] Liệt kê image kèm dung lượng | Images with size
# từ khóa: image đĩa vm rbd danh sách
rbd ls -l -p <pool>
```

## Thông tin (Info)

```bash
# [chỉ đọc] Chi tiết một image | Image details
# từ khóa: image thông tin
rbd info <pool>/<image>

# [chỉ đọc] Dung lượng cấp phát và thực dùng | Provisioned vs used
# từ khóa: đầy thin provisioned dung lượng thực
rbd du -p <pool>

# [chỉ đọc] Ai đang mở image (watcher), để tìm client treo | Watchers (who has it open)
# từ khóa: rbd treo client lock watcher hang
rbd status <pool>/<image>

# [chỉ đọc] Các lock của image | Image locks
# từ khóa: lock treo vm không start
rbd lock ls <pool>/<image>
```

## Snapshot

```bash
# [chỉ đọc] Liệt kê snapshot của image | List snapshots
# từ khóa: snapshot
rbd snap ls <pool>/<image>

# Tạo snapshot | Create snapshot
# từ khóa: tạo snapshot
rbd snap create <pool>/<image>@<snap>

# ⚠ NGUY HIỂM: Quay về snapshot (nguy hiểm) | Roll back (destructive)
# từ khóa: rollback snapshot
rbd snap rollback <pool>/<image>@<snap>

# Bảo vệ snapshot để clone | Protect for cloning
# từ khóa: protect snapshot clone
rbd snap protect <pool>/<image>@<snap>

# Xóa snapshot | Delete snapshot
# từ khóa: xóa snapshot
rbd snap rm <pool>/<image>@<snap>
```

## Nhân bản (Clone)

```bash
# Clone từ snapshot | Clone from snapshot
# từ khóa: clone
rbd clone <pool>/<image>@<snap> <pool>/<clone>

# Tách clone khỏi image gốc | Detach clone from parent
# từ khóa: flatten clone
rbd flatten <pool>/<clone>
```

## Sao chép (Copy)

```bash
# Sao chép image | Copy image
# từ khóa: copy image
rbd cp <src> <dst>

# Xuất image ra file | Export image
# từ khóa: export backup image
rbd export <pool>/<image> <file>

# Nhập file vào image | Import image
# từ khóa: import image
rbd import <file> <pool>/<image>

# Xuất phần thay đổi (incremental) | Incremental export
# từ khóa: incremental diff
rbd export-diff <pool>/<image> <file>
```

## Đổi kích thước (Resize)

```bash
# Đổi kích thước image | Resize image
# từ khóa: resize mở rộng image
rbd resize --size <MiB> <pool>/<image>
```

## Dung lượng (Space)

```bash
# Thu hồi vùng toàn số 0 | Reclaim zeroed space
# từ khóa: sparsify thu hồi dung lượng
rbd sparsify <pool>/<image>
```

## Thùng rác (Trash)

```bash
# [chỉ đọc] Nội dung thùng rác của pool | Trash contents
# từ khóa: trash thùng rác
rbd trash ls -p <pool>

# Chuyển image vào thùng rác | Move to trash
# từ khóa: trash xóa an toàn
rbd trash mv <pool>/<image>

# Khôi phục image từ thùng rác | Restore from trash
# từ khóa: khôi phục image đã xóa
rbd trash restore -p <pool> <image-id>

# ⚠ NGUY HIỂM: Dọn sạch thùng rác (nguy hiểm) | Empty trash (destructive)
# từ khóa: dọn thùng rác
rbd trash purge -p <pool>
```

## Xóa (Delete)

```bash
# ⚠ NGUY HIỂM: Xóa image (nguy hiểm) | Delete image (destructive)
# từ khóa: xóa image đĩa vm
rbd rm <pool>/<image>
```

## Hiệu năng (Perf)

```bash
# [chỉ đọc] Tốc độ IO theo từng image | Per-image IO rates
# từ khóa: io image vm nặng tìm vm ồn
rbd perf image iostat -p <pool>
```

## Đo hiệu năng (Bench)

```bash
# Benchmark image | Image benchmark
# từ khóa: benchmark rbd
rbd bench --io-type write --io-size 4K --io-threads 16 <pool>/<image>
```

## Ánh xạ (Mapping)

```bash
# Map image vào kernel (khi gỡ lỗi) | Kernel map (troubleshooting)
# từ khóa: map unmap kernel gỡ lỗi
rbd map <pool>/<image> / rbd unmap <dev>
```

## Case và runbook dùng lệnh trong nhóm này

- [VM treo IO do image RBD (watcher, lock, blocklist)](../cases/ceph/rbd-hang.md)
