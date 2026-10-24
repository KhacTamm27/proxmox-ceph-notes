# B8 · CRUSH map

[← Mục lục](../../README.md) · Ceph · 19 lệnh

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← B7 Daemon OSD và hiệu năng (admin socket)](../ceph/B07-osd-daemon-and-performance-admin-socket.md) · [B9 Pool →](../ceph/B09-pools.md)

## Xem (View)

```bash
# [chỉ đọc] Cây phân cấp CRUSH | CRUSH hierarchy
# từ khóa: crush cây host rack
ceph osd crush tree

# [chỉ đọc] Các device class | Device classes
# từ khóa: device class ssd hdd
ceph osd crush class ls

# [chỉ đọc] Profile tunables của CRUSH | Tunables profile
# từ khóa: tunables crush
ceph osd crush tunables show
```

## Rule (Rules)

```bash
# [chỉ đọc] Liệt kê rule CRUSH | List rules
# từ khóa: crush rule
ceph osd crush rule ls

# [chỉ đọc] Chi tiết một rule CRUSH | Rule detail
# từ khóa: crush rule chi tiết
ceph osd crush rule dump <rule>

# Tạo rule replicated | Create replicated rule
# từ khóa: tạo rule crush replicated device class
ceph osd crush rule create-replicated <rule> <root> <type> [<class>]

# Tạo rule erasure coding | Create EC rule
# từ khóa: erasure ec rule
ceph osd crush rule create-erasure <rule> <profile>

# ⚠ NGUY HIỂM: Xóa rule (nguy hiểm) | Delete rule (destructive)
# từ khóa: xóa rule crush
ceph osd crush rule rm <rule>
```

## Bucket (Buckets)

```bash
# Tạo bucket CRUSH | Create bucket
# từ khóa: thêm bucket host rack
ceph osd crush add-bucket <name> <type>

# Di chuyển bucket CRUSH | Move bucket
# từ khóa: di chuyển bucket host rack
ceph osd crush move <name> <type>=<parent>

# Thêm cha phụ cho bucket | Add extra parent
# từ khóa: link bucket
ceph osd crush link <name> <type>=<parent>

# Đổi tên bucket | Rename bucket
# từ khóa: đổi tên bucket
ceph osd crush rename-bucket <old> <new>

# ⚠ NGUY HIỂM: Xóa bucket hoặc item (nguy hiểm) | Remove bucket or item (destructive)
# từ khóa: xóa bucket crush
ceph osd crush remove <name>
```

## File map (Map file)

```bash
# [chỉ đọc] Xuất CRUSH map đã biên dịch | Export compiled map
# từ khóa: crush map export backup
ceph osd getcrushmap -o crush.bin

# [chỉ đọc] Giải mã CRUSH map ra text | Decompile
# từ khóa: crush decompile
crushtool -d crush.bin -o crush.txt

# Biên dịch CRUSH map | Compile
# từ khóa: crush compile
crushtool -c crush.txt -o crush.new

# [chỉ đọc] Kiểm tra mapping lỗi | Validate mappings
# từ khóa: crush test mapping
crushtool -i crush.bin --test --rule <n> --num-rep 3 --show-bad-mappings

# [chỉ đọc] Mô phỏng phân bố dữ liệu | Simulate distribution
# từ khóa: crush mô phỏng phân bố
crushtool -i crush.bin --test --rule <n> --num-rep 3 --show-utilization

# Áp dụng CRUSH map mới (có thể gây rebalance) | Apply map (can trigger rebalance)
# từ khóa: áp dụng crush rebalance
ceph osd setcrushmap -i crush.new
```
