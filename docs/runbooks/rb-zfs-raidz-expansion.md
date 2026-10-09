# ZFS RAIDZ: mở rộng vdev bằng cách gắn thêm disk

[← Mục lục](../../README.md) · Runbook

**Mục tiêu:** Mở rộng một RAIDZ vdev hiện có bằng tính năng RAIDZ expansion của OpenZFS khi hệ thống và pool hỗ trợ.

**Điều kiện trước khi làm:** Cần OpenZFS 2.3 trở lên và feature raidz_expansion khả dụng trên pool; xác nhận chính xác phiên bản module đang chạy trên node. Có backup kiểm chứng được, cửa sổ bảo trì phù hợp và disk mới có dung lượng ít nhất bằng disk nhỏ nhất trong vdev.

## Các bước

1. Xác nhận pool khỏe, đúng vdev RAIDZ cần mở rộng và ghi lại serial/WWN của disk mới

```bash
zfs version
zpool status -v <pool-name>
zpool get feature@raidz_expansion <pool-name>
ls -l /dev/disk/by-id/
```

2. Nếu feature chưa bật nhưng được hỗ trợ, bật feature trên đúng pool. Nếu feature không tồn tại hoặc pool degraded, dừng và xử lý điều kiện đó trước

```bash
zpool set feature@raidz_expansion=enabled <pool-name>
```

3. Gắn disk mới vào đúng RAIDZ vdev; xác nhận lại từng placeholder trước khi chạy vì thao tác bắt đầu tái bố trí dữ liệu

```bash
zpool attach <pool-name> <raidz-vdev-name> /dev/disk/by-id/<new-disk-id>
```

4. Theo dõi tiến trình expansion và kiểm tra pool sau khi hoàn tất

```bash
zpool status -v <pool-name>
zpool list <pool-name>
```

## Lưu ý

Không nhầm thao tác này với thêm một top-level vdev bằng `zpool add`. Expansion đọc và ghi lại dữ liệu của RAIDZ vdev nên có thể chạy lâu, tạo tải I/O và kết thúc bằng scrub. RAIDZ1/2/3 vẫn chịu lỗi lần lượt 1/2/3 disk như trước; expansion không tăng mức parity và không thể thu nhỏ/rollback theo cách thông thường. Không dùng disk nhỏ hơn disk nhỏ nhất hiện có. Nếu `zpool get feature@raidz_expansion` báo không nhận biết feature, không thử chạy `zpool attach` như một phép thay disk mirror.

## Nguồn tham khảo

- [OpenZFS zpool-attach: RAIDZ expansion requirements and behavior](https://openzfs.github.io/openzfs-docs/man/master/8/zpool-attach.8.html)

<!-- từ khóa: zfs raidz expansion raidz_expansion zpool attach thêm disk tăng dung lượng pool raidz1 raidz2 proxmox openzfs 2.3 -->
