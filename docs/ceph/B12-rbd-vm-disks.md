# B12 · RBD (VM disks)

[← Mục lục](../../README.md) · Ceph · 26 lệnh

[← B11 Recovery, scrub and config tuning](../ceph/B11-recovery-scrub-and-config-tuning.md) · [B13 RGW and S3 (radosgw-admin) →](../ceph/B13-rgw-and-s3-radosgw-admin.md)

## List

```bash
# Images with size
rbd ls -l -p <pool>
```

## Info

```bash
# Image details
rbd info <pool>/<image>

# Provisioned vs used
rbd du -p <pool>

# Watchers (who has it open)
rbd status <pool>/<image>

# Image locks
rbd lock ls <pool>/<image>
```

## Snapshot

```bash
# List snapshots
rbd snap ls <pool>/<image>

# Create snapshot
rbd snap create <pool>/<image>@<snap>

# ⚠ NGUY HIỂM: Roll back (destructive)
rbd snap rollback <pool>/<image>@<snap>

# Protect for cloning
rbd snap protect <pool>/<image>@<snap>

# Delete snapshot
rbd snap rm <pool>/<image>@<snap>
```

## Clone

```bash
# Clone from snapshot
rbd clone <pool>/<image>@<snap> <pool>/<clone>

# Detach clone from parent
rbd flatten <pool>/<clone>
```

## Copy

```bash
# Copy image
rbd cp <src> <dst>

# Export image
rbd export <pool>/<image> <file>

# Import image
rbd import <file> <pool>/<image>

# Incremental export
rbd export-diff <pool>/<image> <file>
```

## Resize

```bash
# Resize image
rbd resize --size <MiB> <pool>/<image>
```

## Space

```bash
# Reclaim zeroed space
rbd sparsify <pool>/<image>
```

## Trash

```bash
# Trash contents
rbd trash ls -p <pool>

# Move to trash
rbd trash mv <pool>/<image>

# Restore from trash
rbd trash restore -p <pool> <image-id>

# ⚠ NGUY HIỂM: Empty trash (destructive)
rbd trash purge -p <pool>
```

## Delete

```bash
# ⚠ NGUY HIỂM: Delete image (destructive)
rbd rm <pool>/<image>
```

## Perf

```bash
# Per-image IO rates
rbd perf image iostat -p <pool>
```

## Bench

```bash
# Image benchmark
rbd bench --io-type write --io-size 4K --io-threads 16 <pool>/<image>
```

## Mapping

```bash
# Kernel map (troubleshooting)
rbd map <pool>/<image> / rbd unmap <dev>
```
