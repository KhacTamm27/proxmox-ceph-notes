# B5 · OSD flags and maintenance

[← Mục lục](../../README.md) · Ceph · 15 lệnh

[← B4 OSD status](../ceph/B04-osd-status.md) · [B6 OSD lifecycle and devices →](../ceph/B06-osd-lifecycle-and-devices.md)

## Flags

```bash
# Do not mark OSDs out
ceph osd set noout / ceph osd unset noout

# Pause rebalancing
ceph osd set norebalance / ceph osd unset norebalance

# Pause backfill
ceph osd set nobackfill / ceph osd unset nobackfill

# Pause recovery
ceph osd set norecover / ceph osd unset norecover

# Pause scrubs
ceph osd set noscrub / ceph osd set nodeep-scrub

# Pause all client IO (emergency)
ceph osd set pause / ceph osd unset pause
```

## Per subtree

```bash
# Flag one CRUSH node
ceph osd set-group noout <host-or-chassis>

# Clear flag on one CRUSH node
ceph osd unset-group noout <host-or-chassis>
```

## Safety

```bash
# Safe to stop without losing availability
ceph osd ok-to-stop <osd-id>

# Safe to destroy without data loss
ceph osd safe-to-destroy <osd-id>
```

## State

```bash
# Mark out or in
ceph osd out <osd-id> / ceph osd in <osd-id>

# Mark down
ceph osd down <osd-id>
```

## Weight

```bash
# Temporary weight (0 to 1)
ceph osd reweight <osd-id> 0.9

# CRUSH weight
ceph osd crush reweight osd.<id> <weight>

# Auto reweight overfull OSDs
ceph osd reweight-by-utilization
```
