# B12 · RBD (VM disks)

[← Mục lục](../../README.md) · Ceph · 26 lệnh

[← B11 Recovery, scrub and config tuning](../ceph/B11-recovery-scrub-and-config-tuning.md) · [B13 RGW and S3 (radosgw-admin) →](../ceph/B13-rgw-and-s3-radosgw-admin.md)

## List

```bash
# Liệt kê image kèm dung lượng | Images with size
# từ khóa: image đĩa vm rbd danh sách
rbd ls -l -p <pool>
```

## Info

```bash
# Chi tiết một image | Image details
# từ khóa: image thông tin
rbd info <pool>/<image>

# Dung lượng cấp phát và thực dùng | Provisioned vs used
# từ khóa: đầy thin provisioned dung lượng thực
rbd du -p <pool>

# Ai đang mở image (watcher), để tìm client treo | Watchers (who has it open)
# từ khóa: rbd treo client lock watcher hang
rbd status <pool>/<image>

# Các lock của image | Image locks
# từ khóa: lock treo vm không start
rbd lock ls <pool>/<image>
```

## Snapshot

```bash
# Liệt kê snapshot của image | List snapshots
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

## Clone

```bash
# Clone từ snapshot | Clone from snapshot
# từ khóa: clone
rbd clone <pool>/<image>@<snap> <pool>/<clone>

# Tách clone khỏi image gốc | Detach clone from parent
# từ khóa: flatten clone
rbd flatten <pool>/<clone>
```

## Copy

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

## Resize

```bash
# Đổi kích thước image | Resize image
# từ khóa: resize mở rộng image
rbd resize --size <MiB> <pool>/<image>
```

## Space

```bash
# Thu hồi vùng toàn số 0 | Reclaim zeroed space
# từ khóa: sparsify thu hồi dung lượng
rbd sparsify <pool>/<image>
```

## Trash

```bash
# Nội dung thùng rác của pool | Trash contents
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

## Delete

```bash
# ⚠ NGUY HIỂM: Xóa image (nguy hiểm) | Delete image (destructive)
# từ khóa: xóa image đĩa vm
rbd rm <pool>/<image>
```

## Perf

```bash
# Tốc độ IO theo từng image | Per-image IO rates
# từ khóa: io image vm nặng tìm vm ồn
rbd perf image iostat -p <pool>
```

## Bench

```bash
# Benchmark image | Image benchmark
# từ khóa: benchmark rbd
rbd bench --io-type write --io-size 4K --io-threads 16 <pool>/<image>
```

## Mapping

```bash
# Map image vào kernel (khi gỡ lỗi) | Kernel map (troubleshooting)
# từ khóa: map unmap kernel gỡ lỗi
rbd map <pool>/<image> / rbd unmap <dev>
```
