# ZFS: chọn RAID/vdev và tạo pool cho Proxmox

[← Mục lục](../../README.md) · Runbook

**Mục tiêu:** Chọn bố cục ZFS phù hợp workload VM/CT, tạo pool mới an toàn và thêm pool làm storage trong Proxmox VE.

**Điều kiện trước khi làm:** Đây là thao tác tạo pool mới, sẽ khởi tạo các disk đã chọn. Có backup độc lập nếu disk từng chứa dữ liệu. Ghi lại model, dung lượng, serial/WWN, sector size và workload; ưu tiên disk cùng dung lượng, loại và độ bền.

## Các bước

1. Kiểm kê ổ đĩa và xác nhận pool hiện tại; đối chiếu serial/WWN, không dựa vào tên /dev/sdX

```bash
lsblk -o NAME,SIZE,SERIAL,WWN,MODEL,FSTYPE,MOUNTPOINTS
ls -l /dev/disk/by-id/
zpool status -v
```

2. Chọn topology trước khi tạo. Với VM/CT, mirror vdev thường cho IOPS tốt; RAIDZ đổi lấy hiệu quả dung lượng nhưng có thể tăng write amplification cho ZVOL

3. Ví dụ tạo pool mirror mới bằng ID ổ ổn định; thay toàn bộ placeholder và xác nhận đúng hai ổ trống trước khi chạy

```bash
zpool create -o ashift=12 <pool-name> mirror /dev/disk/by-id/<disk-a> /dev/disk/by-id/<disk-b>
```

4. Xác minh trạng thái pool, sau đó thêm vào Datacenter > Storage > Add > ZFS và chọn đúng pool/content

```bash
zpool status -v <pool-name>
zfs list
```

## Lưu ý

Bảng ước lượng (N là số disk trong một vdev; dung lượng thực tế còn phụ thuộc parity, metadata, ashift, compression và mức sử dụng):

| Bố cục | Số disk tối thiểu | Khả năng chịu lỗi | Dung lượng thô khả dụng gần đúng |
|---|---:|---|---:|
| Single | 1 | Không có dự phòng | Gần 1 disk, không có parity |
| Mirror | 2 | Có thể hỏng nhiều disk nếu mỗi mirror còn ít nhất một disk tốt | Gần bằng dung lượng một disk trong từng mirror vdev |
| RAIDZ1 | 3 | 1 disk trong mỗi vdev | N - 1 disk |
| RAIDZ2 | 4 | 2 disk trong mỗi vdev | N - 2 disk |
| RAIDZ3 | 5 | 3 disk trong mỗi vdev | N - 3 disk |
| RAID10 kiểu ZFS | 4 | Ít nhất một disk mỗi cặp mirror; số disk hỏng chịu được tùy cặp | Gần 50% tổng dung lượng disk |

Mirror vdevs thường phù hợp hơn cho workload VM ngẫu nhiên; không có một mức hiệu suất cố định áp dụng cho mọi ổ và mọi workload. RAIDZ parity không phải backup. Topology pool khó đổi sau khi tạo; không thêm một disk lẻ như mirror/RAIDZ mới nếu chưa hiểu rằng mỗi top-level vdev bổ sung ảnh hưởng tới khả năng chịu lỗi của cả pool. `ashift` không thể đổi tại chỗ sau khi tạo. Không dùng `-f` để bỏ qua cảnh báo disk đang có dữ liệu. dRAID và các cấu hình nâng cao cần sizing/kiểm tra riêng, không suy ra cấu hình từ bảng đơn giản này.

## Nguồn tham khảo

- [Proxmox VE Wiki: ZFS on Linux (space, redundancy và workload VM)](https://pve.proxmox.com/wiki/ZFS_on_Linux)

<!-- từ khóa: zfs raid vdev mirror raidz raidz1 raidz2 raidz3 raid10 draid chọn topology dung lượng dự phòng tạo pool zpool create storage proxmox -->
