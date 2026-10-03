# B3 · MGR and modules

[← Mục lục](../../README.md) · Ceph · 12 lệnh

[← B2 MON](../ceph/B02-mon.md) · [B4 OSD status →](../ceph/B04-osd-status.md)

## Status

```bash
# Active and standby MGR
ceph mgr stat

# Module endpoints
ceph mgr services
```

## Control

```bash
# Fail over active MGR
ceph mgr fail
```

## Modules

```bash
# Enabled and available modules
ceph mgr module ls

# Enable exporter
ceph mgr module enable prometheus

# Disable module
ceph mgr module disable <module>
```

## Balancer

```bash
# Balancer state
ceph balancer status

# Set upmap mode
ceph balancer mode upmap

# Toggle balancer
ceph balancer on / ceph balancer off

# Score current distribution
ceph balancer eval
```

## IO

```bash
# Cluster IO rates (iostat module)
ceph iostat
```

## Progress

```bash
# Ongoing recovery progress
ceph progress
```
