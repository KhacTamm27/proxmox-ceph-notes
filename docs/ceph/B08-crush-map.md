# B8 · CRUSH map

[← Mục lục](../../README.md) · Ceph · 19 lệnh

[← B7 OSD daemon and performance (admin socket)](../ceph/B07-osd-daemon-and-performance-admin-socket.md) · [B9 Pools →](../ceph/B09-pools.md)

## View

```bash
# Cây phân cấp CRUSH | CRUSH hierarchy
# từ khóa: crush cây host rack
ceph osd crush tree

# Các device class | Device classes
# từ khóa: device class ssd hdd
ceph osd crush class ls

# Profile tunables của CRUSH | Tunables profile
# từ khóa: tunables crush
ceph osd crush tunables show
```

## Rules

```bash
# Liệt kê rule CRUSH | List rules
# từ khóa: crush rule
ceph osd crush rule ls

# Chi tiết một rule CRUSH | Rule detail
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

## Buckets

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

## Map file

```bash
# Xuất CRUSH map đã biên dịch | Export compiled map
# từ khóa: crush map export backup
ceph osd getcrushmap -o crush.bin

# Giải mã CRUSH map ra text | Decompile
# từ khóa: crush decompile
crushtool -d crush.bin -o crush.txt

# Biên dịch CRUSH map | Compile
# từ khóa: crush compile
crushtool -c crush.txt -o crush.new

# Kiểm tra mapping lỗi | Validate mappings
# từ khóa: crush test mapping
crushtool -i crush.bin --test --rule <n> --num-rep 3 --show-bad-mappings

# Mô phỏng phân bố dữ liệu | Simulate distribution
# từ khóa: crush mô phỏng phân bố
crushtool -i crush.bin --test --rule <n> --num-rep 3 --show-utilization

# Áp dụng CRUSH map mới (có thể gây rebalance) | Apply map (can trigger rebalance)
# từ khóa: áp dụng crush rebalance
ceph osd setcrushmap -i crush.new
```
