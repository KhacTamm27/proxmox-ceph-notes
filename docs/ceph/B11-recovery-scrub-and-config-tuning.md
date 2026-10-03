# B11 · Recovery, scrub and config tuning

[← Mục lục](../../README.md) · Ceph · 11 lệnh

[← B10 Placement groups](../ceph/B10-placement-groups.md) · [B12 RBD (VM disks) →](../ceph/B12-rbd-vm-disks.md)

## Config

```bash
# All centralized settings
ceph config dump

# Read one option
ceph config get <who> <option>

# Set option
ceph config set <who> <option> <value>

# Reset option
ceph config rm <who> <option>
```

## Backfill

```bash
# Limit concurrent backfills
ceph config set osd osd_max_backfills 1
```

## Recovery

```bash
# Limit recovery ops
ceph config set osd osd_recovery_max_active 1

# Throttle recovery on SSD
ceph config set osd osd_recovery_sleep_ssd 0.1
```

## mClock

```bash
# Favor client IO (Quincy and later)
ceph config set osd osd_mclock_profile high_client_ops

# Favor recovery (Quincy and later)
ceph config set osd osd_mclock_profile high_recovery_ops
```

## Scrub

```bash
# Scrub window start
ceph config set osd osd_scrub_begin_hour 22

# Scrub window end
ceph config set osd osd_scrub_end_hour 6
```
