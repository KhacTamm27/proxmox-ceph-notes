# B7 · OSD daemon and performance (admin socket)

[← Mục lục](../../README.md) · Ceph · 9 lệnh

[← B6 OSD lifecycle and devices](../ceph/B06-osd-lifecycle-and-devices.md) · [B8 CRUSH map →](../ceph/B08-crush-map.md)

## Ops

```bash
# Các thao tác đang kẹt trên OSD (chạy trên host của OSD) | Current slow or active ops (admin socket)
# từ khóa: slow ops blocked requests kẹt
ceph daemon osd.<id> dump_ops_in_flight

# Recent slowest ops (admin socket)
ceph daemon osd.<id> dump_historic_ops

# OSD state (admin socket)
ceph daemon osd.<id> status
```

## Perf

```bash
# Internal counters (admin socket)
ceph daemon osd.<id> perf dump

# Live counters (admin socket)
ceph daemonperf osd.<id>
```

## Config

```bash
# Effective config (admin socket)
ceph daemon osd.<id> config show

# Effective config from MON
ceph config show osd.<id>
```

## Bench

```bash
# Raw OSD write bench
ceph tell osd.<id> bench
```

## Heartbeat

```bash
# Thời gian chờ heartbeat trước khi coi OSD là down | Heartbeat grace
# từ khóa: heartbeat flapping down
ceph config get osd osd_heartbeat_grace
```
