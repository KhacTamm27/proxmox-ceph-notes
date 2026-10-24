# B4 · Trạng thái OSD

[← Mục lục](../../README.md) · Ceph · 22 lệnh · tên gốc: OSD status

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← B3 MGR và module](../ceph/B03-mgr-and-modules.md) · [B5 Cờ OSD và bảo trì →](../ceph/B05-osd-flags-and-maintenance.md)

## Cây (Tree)

```bash
# [chỉ đọc] Cây CRUSH kèm trạng thái up/down của từng OSD | CRUSH tree with state
# từ khóa: osd down up tree host vị trí
ceph osd tree

# [chỉ đọc] Chỉ liệt kê các OSD đang down | Only down OSDs
# từ khóa: osd down tìm osd chết
ceph osd tree down

# [chỉ đọc] Cây CRUSH gồm cả shadow tree theo device class | Include device-class shadow trees
# từ khóa: device class ssd hdd shadow
ceph osd tree --show-shadow
```

## Mức sử dụng (Usage)

```bash
# [chỉ đọc] Dung lượng dùng của từng OSD, tìm OSD đầy hoặc lệch | Usage per OSD
# từ khóa: osd đầy nearfull lệch dung lượng
ceph osd df

# [chỉ đọc] Dung lượng theo từng host và OSD | Usage per bucket
# từ khóa: nearfull đầy host osd lệch
ceph osd df tree

# [chỉ đọc] Mức dùng thấp nhất, cao nhất và độ lệch giữa các OSD | Min, max and deviation
# từ khóa: cân bằng lệch utilization
ceph osd utilization
```

## Trạng thái (State)

```bash
# [chỉ đọc] Số OSD up và in, kiểm tra nhanh OSD có rớt không | Up and in counts
# từ khóa: osd up in down flapping
ceph osd stat

# [chỉ đọc] OSD map: flag, ratio, thông tin pool | OSD map, flags, ratios
# từ khóa: flags noout full ratio pool
ceph osd dump

# [chỉ đọc] Danh sách ID OSD | OSD IDs
# từ khóa: osd id
ceph osd ls
```

## Thông tin (Info)

```bash
# [chỉ đọc] Host, thiết bị, phiên bản của một OSD | Host, device, versions
# từ khóa: osd đĩa device host
ceph osd metadata <osd-id>

# [chỉ đọc] OSD này nằm ở host nào | Host and CRUSH location
# từ khóa: tìm osd host vị trí
ceph osd find <osd-id>
```

## Sức khỏe thiết bị (Device health)

```bash
# [chỉ đọc] Liệt kê thiết bị và dự đoán thời gian còn lại | Devices and predicted life expectancy
# từ khóa: devicehealth tuổi thọ đĩa sắp hỏng dự đoán
ceph device ls

# [chỉ đọc] Thiết bị vật lý được OSD sử dụng | Device used by an OSD
# từ khóa: osd device đĩa nào serial
ceph device ls-by-daemon osd.<id>

# [chỉ đọc] Thông tin định danh, vị trí và sức khỏe thiết bị | Device identity, location and health
# từ khóa: device id serial vị trí sức khỏe đĩa
ceph device info <devid>

# [chỉ đọc] Đọc chỉ số sức khỏe thiết bị đã thu thập | Stored device health metrics
# từ khóa: smart metrics devicehealth wear lỗi đĩa
ceph device get-health-metrics <devid>

# Thu thập lại chỉ số sức khỏe của một thiết bị | Refresh metrics for one device
# từ khóa: smart metrics refresh scrape đĩa lỗi cập nhật
ceph device scrape-health-metrics <devid>

# Đánh giá chỉ số và phát cảnh báo thiết bị sắp hỏng | Evaluate device health alerts
# từ khóa: devicehealth cảnh báo disk sắp hỏng predicted failure
ceph device check-health
```

## Hiệu năng (Perf)

```bash
# [chỉ đọc] Độ trễ commit và apply của từng OSD, tìm OSD chậm | Commit and apply latency
# từ khóa: slow ops chậm latency đĩa lag
ceph osd perf
```

## Ngưỡng đầy (Ratios)

```bash
# Đặt ngưỡng nearfull | Nearfull threshold
# từ khóa: nearfull ngưỡng ratio
ceph osd set-nearfull-ratio 0.85

# Đặt ngưỡng backfillfull, vượt ngưỡng thì dừng backfill | Backfill-full threshold
# từ khóa: backfillfull ratio
ceph osd set-backfillfull-ratio 0.90

# Đặt ngưỡng full, vượt thì chặn ghi | Full threshold
# từ khóa: full đầy chặn ghi ratio
ceph osd set-full-ratio 0.95
```

## Danh sách chặn (Blocklist)

```bash
# [chỉ đọc] Client đang bị chặn (blocklist) | Blocklisted clients
# từ khóa: blocklist client treo rbd hang
ceph osd blocklist ls
```

## Case và runbook dùng lệnh trong nhóm này

- [Nâng cấp Proxmox VE 8 lên 9 trong cluster có Ceph](../cases/pve/pve-upgrade-8to9.md)
- [PVE host hỏng đĩa boot, không có backup cấu hình: kiểm kê và dựng lại node](../cases/pve/pve-host-rebuild-no-config-backup.md)
- [Xóa node Proxmox khỏi cluster an toàn (VM, HA và Ceph)](../runbooks/rb-pve-remove-node.md)
- [OSD down hoặc up/down liên tục (flapping)](../cases/ceph/osd-down-flapping.md)
- [Thay đĩa OSD hỏng](../cases/ceph/osd-replace-disk.md)
- [PG degraded / undersized, recovery chậm](../cases/ceph/pg-degraded-recovery.md)
- [OSD không lên sau reboot](../cases/ceph/osd-wont-start.md)
- [PG down, peering kẹt hoặc unfound objects (mất nhiều OSD)](../cases/ceph/pg-down-incomplete.md)
- [Một node chết hẳn (hỏng phần cứng): khôi phục dịch vụ](../cases/pve/node-dead-recovery.md)
- [Cảnh báo too many / too few PGs, chỉnh pg_num](../cases/ceph/pg-count.md)
- [Ceph nearfull / full / pool đầy](../cases/ceph/nearfull-full.md)
- [Cluster đầy khẩn cấp: ghi bị chặn (OSD_FULL), backfill_toofull](../cases/ceph/cluster-full-emergency.md)
- [Nâng cấp Ceph Quincy 17.2.8 → Reef 18.2.8 → Squid 19.2.4 trên PVE 8.4 (3 node, có CephFS)](../runbooks/rb-ceph-upgrade-quincy-reef-squid.md)
- [Bảo trì hoặc reboot một node Proxmox + Ceph](../cases/pve/node-maintenance.md)
- [Nâng cấp Ceph trên Proxmox (ví dụ Reef lên Squid)](../cases/ceph/ceph-upgrade-pve.md)
- [Bảo trì production: tắt HA và đặt cờ bảo trì Ceph trước khi tắt node](../runbooks/rb-prod-maintenance.md)
- [Cảnh báo PG không được scrub / deep-scrub kịp thời](../cases/ceph/deep-scrub-late.md)
- [Cờ bảo trì Ceph còn sót sau bảo trì (noout, noscrub, norecover...)](../cases/ceph/maintenance-flags-left.md)
- [Ceph cảnh báo OSD device có nguy cơ hỏng](../cases/ceph/osd-device-health-warning.md)
- [Slow ops / blocked requests (Ceph chậm, IO bị chặn)](../cases/ceph/slow-ops.md)
- [Mạng Ceph: MTU không khớp, nghẽn hoặc rớt gói](../cases/ceph/network-mtu.md)
- [Latency OSD cao, IOPS thấp do SSD consumer (không có PLP)](../cases/ceph/osd-latency-consumer-ssd.md)
- [VM treo IO do image RBD (watcher, lock, blocklist)](../cases/ceph/rbd-hang.md)
