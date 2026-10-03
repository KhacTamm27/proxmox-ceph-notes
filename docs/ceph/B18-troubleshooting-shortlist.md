# B18 · Troubleshooting shortlist

[← Mục lục](../../README.md) · Ceph · 19 lệnh

[← B17 Upgrade and compatibility](../ceph/B17-upgrade-and-compatibility.md)

## HEALTH_WARN

```bash
# Find the exact warning
ceph health detail
```

## Slow ops

```bash
# Which ops are stuck (admin socket)
ceph daemon osd.<id> dump_ops_in_flight

# OSDs with high latency
ceph osd perf
```

## OSD flapping

```bash
# Up and in counts
ceph osd stat

# OSD log around the flap
journalctl -u ceph-osd@<osd-id> --since "1 hour ago"

# Heartbeat grace in use
ceph config get osd osd_heartbeat_grace

# NIC errors on OSD host
ethtool -S <if>
```

## PGs stuck

```bash
# Find inactive PGs
ceph pg dump_stuck inactive

# See why a PG is stuck
ceph pg <pgid> query
```

## Undersized

```bash
# PGs missing replicas
ceph pg ls undersized
```

## Nearfull

```bash
# Find the full OSD or host
ceph osd df tree
```

## Large omap

```bash
# Names pool and object
ceph health detail

# Buckets over shard limit
radosgw-admin bucket limit check

# Count keys in object
rados -p <pool> listomapkeys <object>
```

## Clock skew

```bash
# MON skew
ceph time-sync-status

# Local NTP offset
chronyc tracking
```

## MON down

```bash
# Who is in quorum
ceph quorum_status -f json-pretty
```

## Client hang

```bash
# Watchers on the image
rbd status <pool>/<image>

# Blocklisted client addresses
ceph osd blocklist ls
```
