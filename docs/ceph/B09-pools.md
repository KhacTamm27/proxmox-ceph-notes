# B9 · Pools

[← Mục lục](../../README.md) · Ceph · 18 lệnh

[← B8 CRUSH map](../ceph/B08-crush-map.md) · [B10 Placement groups →](../ceph/B10-placement-groups.md)

## View

```bash
# Pools with settings
ceph osd pool ls detail

# All settings of a pool
ceph osd pool get <pool> all

# Client and recovery IO per pool
ceph osd pool stats
```

## Create

```bash
# Create pool
ceph osd pool create <pool> <pg_num>

# Tag pool application
ceph osd pool application enable <pool> rbd
```

## Settings

```bash
# Replica count
ceph osd pool set <pool> size 3

# Minimum replicas for IO
ceph osd pool set <pool> min_size 2

# Change placement rule
ceph osd pool set <pool> crush_rule <rule>

# Autoscaler
ceph osd pool set <pool> pg_autoscale_mode on

# Expected share of capacity
ceph osd pool set <pool> target_size_ratio 0.9

# Protect from deletion
ceph osd pool set <pool> nodelete true
```

## Autoscale

```bash
# PG autoscaler view
ceph osd pool autoscale-status
```

## Quota

```bash
# Set quota
ceph osd pool set-quota <pool> max_bytes <n>

# Show quota
ceph osd pool get-quota <pool>
```

## Rename

```bash
# Rename pool
ceph osd pool rename <old> <new>
```

## Delete

```bash
# Allow deletion
ceph config set mon mon_allow_pool_delete true

# ⚠ NGUY HIỂM: Delete pool (destructive)
ceph osd pool delete <pool> <pool> --yes-i-really-really-mean-it
```

## Usage

```bash
# Objects and bytes per pool
rados df
```
