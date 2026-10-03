# B1 · Health and status

[← Mục lục](../../README.md) · Ceph · 14 lệnh

[B2 MON →](../ceph/B02-mon.md)

## Overview

```bash
# Cluster summary
ceph -s

# Live event stream
ceph -w
```

## Health

```bash
# Warnings with detail
ceph health detail

# Machine-readable status
ceph status --format json-pretty
```

## Capacity

```bash
# Raw and per-pool usage
ceph df

# Extended usage and quotas
ceph df detail
```

## Versions

```bash
# Daemon versions
ceph versions

# Cluster ID
ceph fsid
```

## Log

```bash
# Recent cluster log
ceph log last 50
```

## Crash

```bash
# Recorded daemon crashes
ceph crash ls

# Crash details
ceph crash info <crash-id>

# Acknowledge crashes
ceph crash archive-all
```

## Time

```bash
# MON clock skew
ceph time-sync-status
```

## Report

```bash
# Full cluster report
ceph report
```
