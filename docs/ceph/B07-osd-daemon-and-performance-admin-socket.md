# B7 · Daemon OSD và hiệu năng (admin socket)

[← Mục lục](../../README.md) · Ceph · 9 lệnh · tên gốc: OSD daemon and performance (admin socket)

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← B6 Vòng đời OSD và thiết bị](../ceph/B06-osd-lifecycle-and-devices.md) · [B8 CRUSH map →](../ceph/B08-crush-map.md)

## Thao tác (ops) (Ops)

```bash
# [chỉ đọc] Các thao tác đang kẹt trên OSD (chạy trên host của OSD) | Current slow or active ops (admin socket)
# từ khóa: slow ops blocked requests kẹt
ceph daemon osd.<id> dump_ops_in_flight

# [chỉ đọc] Các thao tác chậm nhất gần đây (admin socket) | Recent slowest ops (admin socket)
# từ khóa: slow ops chậm thao tác lịch sử
ceph daemon osd.<id> dump_historic_ops

# [chỉ đọc] Trạng thái OSD (admin socket) | OSD state (admin socket)
# từ khóa: osd trạng thái socket
ceph daemon osd.<id> status
```

## Hiệu năng (Perf)

```bash
# [chỉ đọc] Bộ đếm hiệu năng nội bộ (admin socket) | Internal counters (admin socket)
# từ khóa: perf counter hiệu năng
ceph daemon osd.<id> perf dump

# [chỉ đọc] Bộ đếm trực tiếp theo thời gian thực | Live counters (admin socket)
# từ khóa: perf realtime
ceph daemonperf osd.<id>
```

## Cấu hình (Config)

```bash
# [chỉ đọc] Cấu hình đang áp dụng của OSD (admin socket) | Effective config (admin socket)
# từ khóa: config osd hiệu lực
ceph daemon osd.<id> config show

# [chỉ đọc] Cấu hình đang áp dụng, lấy từ MON | Effective config from MON
# từ khóa: config osd hiệu lực
ceph config show osd.<id>
```

## Đo hiệu năng (Bench)

```bash
# Benchmark ghi thô của OSD | Raw OSD write bench
# từ khóa: benchmark osd iops đĩa chậm
ceph tell osd.<id> bench
```

## Heartbeat

```bash
# [chỉ đọc] Thời gian chờ heartbeat trước khi coi OSD là down | Heartbeat grace
# từ khóa: heartbeat flapping down
ceph config get osd osd_heartbeat_grace
```

## Case và runbook dùng lệnh trong nhóm này

- [Slow ops / blocked requests (Ceph chậm, IO bị chặn)](../cases/ceph/slow-ops.md)
- [BLUEFS_SPILLOVER: metadata RocksDB tràn sang đĩa chậm](../cases/ceph/bluefs-spillover.md)
- [Latency OSD cao, IOPS thấp do SSD consumer (không có PLP)](../cases/ceph/osd-latency-consumer-ssd.md)
- [OSD down hoặc up/down liên tục (flapping)](../cases/ceph/osd-down-flapping.md)
