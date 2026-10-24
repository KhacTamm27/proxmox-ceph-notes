# B3 · MGR và module

[← Mục lục](../../README.md) · Ceph · 12 lệnh · tên gốc: MGR and modules

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← B2 MON](../ceph/B02-mon.md) · [B4 Trạng thái OSD →](../ceph/B04-osd-status.md)

## Trạng thái (Status)

```bash
# [chỉ đọc] MGR đang active và standby | Active and standby MGR
# từ khóa: mgr active standby
ceph mgr stat

# [chỉ đọc] Địa chỉ các module (dashboard, prometheus) | Module endpoints
# từ khóa: mgr dashboard prometheus url
ceph mgr services
```

## Điều khiển (Control)

```bash
# Chuyển MGR active sang node khác | Fail over active MGR
# từ khóa: mgr treo failover
ceph mgr fail
```

## Module (Modules)

```bash
# [chỉ đọc] Module MGR đã bật và có sẵn | Enabled and available modules
# từ khóa: mgr module
ceph mgr module ls

# Bật exporter prometheus | Enable exporter
# từ khóa: prometheus monitoring giám sát
ceph mgr module enable prometheus

# Tắt một module MGR | Disable module
# từ khóa: tắt module mgr
ceph mgr module disable <module>
```

## Cân bằng (Balancer)

```bash
# [chỉ đọc] Trạng thái balancer | Balancer state
# từ khóa: balancer cân bằng pg
ceph balancer status

# Đặt chế độ upmap cho balancer | Set upmap mode
# từ khóa: balancer upmap
ceph balancer mode upmap

# Bật hoặc tắt balancer | Toggle balancer
# từ khóa: bật tắt balancer
ceph balancer on / ceph balancer off

# [chỉ đọc] Chấm điểm độ cân bằng hiện tại | Score current distribution
# từ khóa: balancer lệch dung lượng
ceph balancer eval
```

## IO

```bash
# [chỉ đọc] Tốc độ IO của cluster | Cluster IO rates (iostat module)
# từ khóa: io tốc độ throughput
ceph iostat
```

## Tiến độ (Progress)

```bash
# [chỉ đọc] Tiến độ recovery đang chạy | Ongoing recovery progress
# từ khóa: recovery tiến độ progress
ceph progress
```
