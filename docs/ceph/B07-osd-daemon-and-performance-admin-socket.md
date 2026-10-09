# B7 · OSD daemon and performance (admin socket)

[← Mục lục](../../README.md) · Ceph · 9 lệnh

[← B6 OSD lifecycle and devices](../ceph/B06-osd-lifecycle-and-devices.md) · [B8 CRUSH map →](../ceph/B08-crush-map.md)

## Ops

```bash
# Các thao tác đang kẹt trên OSD (chạy trên host của OSD) | Current slow or active ops (admin socket)
# từ khóa: slow ops blocked requests kẹt
ceph daemon osd.<id> dump_ops_in_flight

# Các thao tác chậm nhất gần đây (admin socket) | Recent slowest ops (admin socket)
# từ khóa: slow ops chậm thao tác lịch sử
ceph daemon osd.<id> dump_historic_ops

# Trạng thái OSD (admin socket) | OSD state (admin socket)
# từ khóa: osd trạng thái socket
ceph daemon osd.<id> status
```

## Perf

```bash
# Bộ đếm hiệu năng nội bộ (admin socket) | Internal counters (admin socket)
# từ khóa: perf counter hiệu năng
ceph daemon osd.<id> perf dump

# Bộ đếm trực tiếp theo thời gian thực | Live counters (admin socket)
# từ khóa: perf realtime
ceph daemonperf osd.<id>
```

## Config

```bash
# Cấu hình đang áp dụng của OSD (admin socket) | Effective config (admin socket)
# từ khóa: config osd hiệu lực
ceph daemon osd.<id> config show

# Cấu hình đang áp dụng, lấy từ MON | Effective config from MON
# từ khóa: config osd hiệu lực
ceph config show osd.<id>
```

## Bench

```bash
# Benchmark ghi thô của OSD | Raw OSD write bench
# từ khóa: benchmark osd iops đĩa chậm
ceph tell osd.<id> bench
```

## Heartbeat

```bash
# Thời gian chờ heartbeat trước khi coi OSD là down | Heartbeat grace
# từ khóa: heartbeat flapping down
ceph config get osd osd_heartbeat_grace
```
