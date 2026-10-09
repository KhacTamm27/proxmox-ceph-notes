# ZFS: thêm hoặc gỡ L2ARC cache và hot spare

[← Mục lục](../../README.md) · Runbook

**Mục tiêu:** Quản lý thiết bị cache đọc L2ARC hoặc hot spare cho ZFS pool mà không nhầm với disk dữ liệu, SLOG hay backup.

**Điều kiện trước khi làm:** Pool phải khỏe, có backup phù hợp và đã xác định chính xác thiết bị theo serial/WWN. Thiết bị spare nên đủ lớn để thay disk cần bảo vệ. Xác nhận loại vdev và cách bỏ thiết bị theo phiên bản OpenZFS trước khi thao tác.

## Các bước

1. Kiểm tra pool, thiết bị đang tham gia và đường dẫn ổn định

```bash
zpool status -P <pool-name>
ls -l /dev/disk/by-id/
```

2. Thêm thiết bị L2ARC cache đọc hoặc hot spare vào đúng pool. Chọn đúng một lệnh phù hợp với vai trò; không chạy cả hai nếu chỉ triển khai một thiết bị

```bash
zpool add <pool-name> cache /dev/disk/by-id/<cache-disk-id>
zpool add <pool-name> spare /dev/disk/by-id/<spare-disk-id>
```

3. Xác minh vai trò thiết bị trong pool

```bash
zpool status -P <pool-name>
```

4. Khi gỡ, chỉ chọn đúng device đang hiển thị dưới cache/spares; không chọn leaf device của data vdev

```bash
zpool remove <pool-name> /dev/disk/by-id/<exact-cache-or-spare-id>
zpool status -P <pool-name>
```

## Lưu ý

L2ARC là read cache, không phải write cache, metadata repair hay nơi lưu dữ liệu bền vững; cache device lỗi thường không làm mất dữ liệu pool. SLOG (separate intent log) là vai trò khác và không nên gọi chung là cache. Hot spare chỉ là thiết bị dự phòng; pool vẫn cần redundancy phù hợp và spare không thay thế backup. Có thể cấu hình autoreplace riêng, nhưng không bắt buộc chỉ để đăng ký hot spare: `autoreplace` điều khiển nhận diện thiết bị thay cùng vị trí, không phải lệnh thêm spare. Nếu spare đang được dùng để thay disk lỗi, không gỡ spare cho đến khi replacement/resilver hoàn tất và `zpool status` xác nhận trạng thái an toàn. Không dùng `/dev/sdX` làm danh tính ổ; không gỡ device nào nếu `zpool status -P` không xác nhận rõ đó là cache hoặc spare.

## Nguồn tham khảo

- [OpenZFS zpoolconcepts: cache and spare devices](https://openzfs.github.io/openzfs-docs/man/master/7/zpoolconcepts.7.html)

<!-- từ khóa: zfs l2arc cache spare hot spare zpool add remove disk dự phòng tăng tốc cache autoreplace -->
