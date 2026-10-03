# B4 · OSD status

[← Mục lục](../../README.md) · Ceph · 16 lệnh

[← B3 MGR and modules](../ceph/B03-mgr-and-modules.md) · [B5 OSD flags and maintenance →](../ceph/B05-osd-flags-and-maintenance.md)

## Tree

```bash
# Cây CRUSH kèm trạng thái up/down của từng OSD | CRUSH tree with state
# từ khóa: osd down up tree host vị trí
ceph osd tree

# Chỉ liệt kê các OSD đang down | Only down OSDs
# từ khóa: osd down tìm osd chết
ceph osd tree down

# Cây CRUSH gồm cả shadow tree theo device class | Include device-class shadow trees
# từ khóa: device class ssd hdd shadow
ceph osd tree --show-shadow
```

## Usage

```bash
# Dung lượng dùng của từng OSD, tìm OSD đầy hoặc lệch | Usage per OSD
# từ khóa: osd đầy nearfull lệch dung lượng
ceph osd df

# Dung lượng theo từng host và OSD | Usage per bucket
# từ khóa: nearfull đầy host osd lệch
ceph osd df tree

# Mức dùng thấp nhất, cao nhất và độ lệch giữa các OSD | Min, max and deviation
# từ khóa: cân bằng lệch utilization
ceph osd utilization
```

## State

```bash
# Số OSD up và in, kiểm tra nhanh OSD có rớt không | Up and in counts
# từ khóa: osd up in down flapping
ceph osd stat

# OSD map: flag, ratio, thông tin pool | OSD map, flags, ratios
# từ khóa: flags noout full ratio pool
ceph osd dump

# Danh sách ID OSD | OSD IDs
# từ khóa: osd id
ceph osd ls
```

## Info

```bash
# Host, thiết bị, phiên bản của một OSD | Host, device, versions
# từ khóa: osd đĩa device host
ceph osd metadata <osd-id>

# OSD này nằm ở host nào | Host and CRUSH location
# từ khóa: tìm osd host vị trí
ceph osd find <osd-id>
```

## Perf

```bash
# Độ trễ commit và apply của từng OSD, tìm OSD chậm | Commit and apply latency
# từ khóa: slow ops chậm latency đĩa lag
ceph osd perf
```

## Ratios

```bash
# Đặt ngưỡng nearfull | Nearfull threshold
# từ khóa: nearfull ngưỡng ratio
ceph osd set-nearfull-ratio 0.85

# Đặt ngưỡng backfillfull, vượt ngưỡng thì dừng backfill | Backfill-full threshold
# từ khóa: backfillfull ratio
ceph osd set-backfillfull-ratio 0.90

# Đặt ngưỡng full, vượt thì chặn ghi | Full threshold
# từ khóa: full đầy chặn ghi ratio
ceph osd set-full-ratio 0.95
```

## Blocklist

```bash
# Client đang bị chặn (blocklist) | Blocklisted clients
# từ khóa: blocklist client treo rbd hang
ceph osd blocklist ls
```
