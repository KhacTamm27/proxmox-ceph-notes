# B2 · MON

[← Mục lục](../../README.md) · Ceph · 8 lệnh

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← B1 Sức khỏe và trạng thái](../ceph/B01-health-and-status.md) · [B3 MGR và module →](../ceph/B03-mgr-and-modules.md)

## Trạng thái (Status)

```bash
# [chỉ đọc] Tóm tắt MON và quorum | MON summary
# từ khóa: mon quorum monitor
ceph mon stat

# [chỉ đọc] Xem MON map | MON map
# từ khóa: monmap địa chỉ mon
ceph mon dump
```

## Quorum

```bash
# [chỉ đọc] Chi tiết quorum MON, biết MON nào đang vắng | Quorum detail
# từ khóa: mon down quorum mất mon
ceph quorum_status -f json-pretty
```

## Admin socket

```bash
# [chỉ đọc] Trạng thái MON ngay trên host (khi ceph -s không phản hồi) | Local MON status (admin socket)
# từ khóa: mon không phản hồi admin socket treo
ceph daemon mon.<id> mon_status
```

## Bảo trì (Maintenance)

```bash
# Nén store của MON khi MON phình to | Compact MON store
# từ khóa: mon store lớn compact đầy disk
ceph tell mon.<id> compact
```

## Tính năng (Features)

```bash
# [chỉ đọc] Tính năng MON đang bật | MON features
# từ khóa: feature
ceph mon feature ls
```

## Giao thức (Protocol)

```bash
# Bật giao thức msgr2 | Enable msgr2
# từ khóa: msgr2 v2 nâng cấp
ceph mon enable-msgr2
```

## Map

```bash
# [chỉ đọc] Xuất MON map ra file | Export MON map
# từ khóa: monmap backup
ceph mon getmap -o monmap.bin
```

## Case và runbook dùng lệnh trong nhóm này

- [Nâng cấp Ceph Quincy 17.2.8 → Reef 18.2.8 → Squid 19.2.4 trên PVE 8.4 (3 node, có CephFS)](../runbooks/rb-ceph-upgrade-quincy-reef-squid.md)
- [Nâng cấp Ceph trên Proxmox (ví dụ Reef lên Squid)](../cases/ceph/ceph-upgrade-pve.md)
- [PVE host hỏng đĩa boot, không có backup cấu hình: kiểm kê và dựng lại node](../cases/pve/pve-host-rebuild-no-config-backup.md)
- [Xóa node Proxmox khỏi cluster an toàn (VM, HA và Ceph)](../runbooks/rb-pve-remove-node.md)
- [MON down, ceph -s treo hoặc mất quorum Ceph](../cases/ceph/mon-down.md)
