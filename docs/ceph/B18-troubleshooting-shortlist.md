# B18 · Troubleshooting shortlist

[← Mục lục](../../README.md) · Ceph · 19 lệnh

[← B17 Upgrade and compatibility](../ceph/B17-upgrade-and-compatibility.md)

## HEALTH_WARN

```bash
# Chi tiết từng cảnh báo HEALTH_WARN/ERR, cho biết PG/OSD/pool nào lỗi | Find the exact warning
# từ khóa: warn error cảnh báo lỗi health nearfull inconsistent large omap
ceph health detail
```

## Slow ops

```bash
# Các thao tác đang kẹt trên OSD (chạy trên host của OSD) | Which ops are stuck (admin socket)
# từ khóa: slow ops blocked requests kẹt
ceph daemon osd.<id> dump_ops_in_flight

# Độ trễ commit và apply của từng OSD, tìm OSD chậm | OSDs with high latency
# từ khóa: slow ops chậm latency đĩa lag
ceph osd perf
```

## OSD flapping

```bash
# Số OSD up và in, kiểm tra nhanh OSD có rớt không | Up and in counts
# từ khóa: osd up in down flapping
ceph osd stat

# Log OSD trong 1 giờ gần nhất, tìm nguyên nhân rớt OSD | OSD log around the flap
# từ khóa: osd down flapping log crash oom
journalctl -u ceph-osd@<osd-id> --since "1 hour ago"

# Thời gian chờ heartbeat trước khi coi OSD là down | Heartbeat grace in use
# từ khóa: heartbeat flapping down
ceph config get osd osd_heartbeat_grace

# Thống kê lỗi card mạng trên host OSD | NIC errors on OSD host
# từ khóa: nic lỗi mạng drop crc flapping
ethtool -S <if>
```

## PGs stuck

```bash
# PG kẹt inactive (không phục vụ IO) | Find inactive PGs
# từ khóa: pg inactive stuck treo mất dữ liệu
ceph pg dump_stuck inactive

# Trạng thái chi tiết của PG, lý do bị kẹt | See why a PG is stuck
# từ khóa: pg stuck peering incomplete lý do
ceph pg <pgid> query
```

## Undersized

```bash
# PG đang thiếu bản sao | PGs missing replicas
# từ khóa: undersized degraded
ceph pg ls undersized
```

## Nearfull

```bash
# Dung lượng theo từng host và OSD | Find the full OSD or host
# từ khóa: nearfull đầy host osd lệch
ceph osd df tree
```

## Large omap

```bash
# Chi tiết từng cảnh báo HEALTH_WARN/ERR, cho biết PG/OSD/pool nào lỗi | Names pool and object
# từ khóa: warn error cảnh báo lỗi health nearfull inconsistent large omap
ceph health detail

# Bucket vượt giới hạn shard (nguyên nhân large omap) | Buckets over shard limit
# từ khóa: large omap shard bucket index rgw
radosgw-admin bucket limit check

# Đếm key omap của object nghi lớn | Count keys in object
# từ khóa: large omap object
rados -p <pool> listomapkeys <object>
```

## Clock skew

```bash
# Độ lệch giờ giữa các MON | MON skew
# từ khóa: clock skew lệch giờ mất đồng bộ giờ ntp
ceph time-sync-status

# Độ lệch NTP trên máy hiện tại | Local NTP offset
# từ khóa: ntp chrony lệch giờ clock skew
chronyc tracking
```

## MON down

```bash
# Chi tiết quorum MON, biết MON nào đang vắng | Who is in quorum
# từ khóa: mon down quorum mất mon
ceph quorum_status -f json-pretty
```

## Client hang

```bash
# Ai đang mở image (watcher), để tìm client treo | Watchers on the image
# từ khóa: rbd treo client lock watcher hang
rbd status <pool>/<image>

# Client đang bị chặn (blocklist) | Blocklisted client addresses
# từ khóa: blocklist client treo rbd hang
ceph osd blocklist ls
```
