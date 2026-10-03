# B2 · MON

[← Mục lục](../../README.md) · Ceph · 8 lệnh

[← B1 Health and status](../ceph/B01-health-and-status.md) · [B3 MGR and modules →](../ceph/B03-mgr-and-modules.md)

## Status

```bash
# Tóm tắt MON và quorum | MON summary
# từ khóa: mon quorum monitor
ceph mon stat

# Xem MON map | MON map
# từ khóa: monmap địa chỉ mon
ceph mon dump
```

## Quorum

```bash
# Chi tiết quorum MON, biết MON nào đang vắng | Quorum detail
# từ khóa: mon down quorum mất mon
ceph quorum_status -f json-pretty
```

## Admin socket

```bash
# Trạng thái MON ngay trên host (khi ceph -s không phản hồi) | Local MON status (admin socket)
# từ khóa: mon không phản hồi admin socket treo
ceph daemon mon.<id> mon_status
```

## Maintenance

```bash
# Nén store của MON khi MON phình to | Compact MON store
# từ khóa: mon store lớn compact đầy disk
ceph tell mon.<id> compact
```

## Features

```bash
# Tính năng MON đang bật | MON features
# từ khóa: feature
ceph mon feature ls
```

## Protocol

```bash
# Bật giao thức msgr2 | Enable msgr2
# từ khóa: msgr2 v2 nâng cấp
ceph mon enable-msgr2
```

## Map

```bash
# Xuất MON map ra file | Export MON map
# từ khóa: monmap backup
ceph mon getmap -o monmap.bin
```
