# B4 · OSD status

[← Mục lục](../../README.md) · Ceph · 16 lệnh

[← B3 MGR and modules](../ceph/B03-mgr-and-modules.md) · [B5 OSD flags and maintenance →](../ceph/B05-osd-flags-and-maintenance.md)

## Tree

```bash
# CRUSH tree with state
ceph osd tree

# Only down OSDs
ceph osd tree down

# Include device-class shadow trees
ceph osd tree --show-shadow
```

## Usage

```bash
# Usage per OSD
ceph osd df

# Usage per bucket
ceph osd df tree

# Min, max and deviation
ceph osd utilization
```

## State

```bash
# Up and in counts
ceph osd stat

# OSD map, flags, ratios
ceph osd dump

# OSD IDs
ceph osd ls
```

## Info

```bash
# Host, device, versions
ceph osd metadata <osd-id>

# Host and CRUSH location
ceph osd find <osd-id>
```

## Perf

```bash
# Commit and apply latency
ceph osd perf
```

## Ratios

```bash
# Nearfull threshold
ceph osd set-nearfull-ratio 0.85

# Backfill-full threshold
ceph osd set-backfillfull-ratio 0.90

# Full threshold
ceph osd set-full-ratio 0.95
```

## Blocklist

```bash
# Blocklisted clients
ceph osd blocklist ls
```
