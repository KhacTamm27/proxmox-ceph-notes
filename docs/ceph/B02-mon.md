# B2 · MON

[← Mục lục](../../README.md) · Ceph · 8 lệnh

[← B1 Health and status](../ceph/B01-health-and-status.md) · [B3 MGR and modules →](../ceph/B03-mgr-and-modules.md)

## Status

```bash
# MON summary
ceph mon stat

# MON map
ceph mon dump
```

## Quorum

```bash
# Quorum detail
ceph quorum_status -f json-pretty
```

## Admin socket

```bash
# Local MON status (admin socket)
ceph daemon mon.<id> mon_status
```

## Maintenance

```bash
# Compact MON store
ceph tell mon.<id> compact
```

## Features

```bash
# MON features
ceph mon feature ls
```

## Protocol

```bash
# Enable msgr2
ceph mon enable-msgr2
```

## Map

```bash
# Export MON map
ceph mon getmap -o monmap.bin
```
