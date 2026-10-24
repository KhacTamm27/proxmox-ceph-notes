# B1 · Sức khỏe và trạng thái

[← Mục lục](../../README.md) · Ceph · 14 lệnh · tên gốc: Health and status

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[B2 MON →](../ceph/B02-mon.md)

## Tổng quan (Overview)

```bash
# [chỉ đọc] Tổng quan sức khỏe cluster Ceph, lệnh đầu tiên cần chạy | Cluster summary
# từ khóa: status health tổng quan kiểm tra nhanh
ceph -s

# [chỉ đọc] Xem sự kiện cluster chạy liên tục (recovery, scrub, lỗi) | Live event stream
# từ khóa: watch live theo dõi realtime
ceph -w
```

## Sức khỏe (Health)

```bash
# [chỉ đọc] Chi tiết từng cảnh báo HEALTH_WARN/ERR, cho biết PG/OSD/pool nào lỗi | Warnings with detail
# từ khóa: warn error cảnh báo lỗi health nearfull inconsistent large omap
ceph health detail

# [chỉ đọc] Trạng thái cluster dạng JSON để đưa vào script | Machine-readable status
# từ khóa: json script monitoring
ceph status --format json-pretty
```

## Dung lượng (Capacity)

```bash
# [chỉ đọc] Dung lượng thô và theo từng pool | Raw and per-pool usage
# từ khóa: đầy disk dung lượng usage capacity full
ceph df

# [chỉ đọc] Dung lượng mở rộng kèm quota | Extended usage and quotas
# từ khóa: quota dung lượng pool
ceph df detail
```

## Phiên bản (Versions)

```bash
# [chỉ đọc] Phiên bản các daemon, kiểm tra lệch version khi nâng cấp | Daemon versions
# từ khóa: version nâng cấp upgrade mixed
ceph versions

# [chỉ đọc] Lấy ID của cluster | Cluster ID
# từ khóa: fsid cluster id
ceph fsid
```

## Log

```bash
# [chỉ đọc] 50 dòng log cluster gần nhất | Recent cluster log
# từ khóa: log gần đây cluster log
ceph log last 50
```

## Crash

```bash
# [chỉ đọc] Danh sách daemon đã crash (cảnh báo RECENT_CRASH) | Recorded daemon crashes
# từ khóa: crash daemon chết recent_crash
ceph crash ls

# [chỉ đọc] Chi tiết một lần crash | Crash details
# từ khóa: crash backtrace
ceph crash info <crash-id>

# Xác nhận đã xem mọi crash để hết cảnh báo | Acknowledge crashes
# từ khóa: xóa cảnh báo crash archive
ceph crash archive-all
```

## Thời gian (Time)

```bash
# [chỉ đọc] Độ lệch giờ giữa các MON | MON clock skew
# từ khóa: clock skew lệch giờ mất đồng bộ giờ ntp
ceph time-sync-status
```

## Báo cáo (Report)

```bash
# [chỉ đọc] Xuất báo cáo đầy đủ để gửi hỗ trợ hoặc phân tích | Full cluster report
# từ khóa: report báo cáo debug
ceph report
```

## Case và runbook dùng lệnh trong nhóm này

- [Slow ops / blocked requests (Ceph chậm, IO bị chặn)](../cases/ceph/slow-ops.md)
- [Thay đĩa OSD hỏng](../cases/ceph/osd-replace-disk.md)
- [Ceph cảnh báo OSD device có nguy cơ hỏng](../cases/ceph/osd-device-health-warning.md)
- [Bảo trì hoặc reboot một node Proxmox + Ceph](../cases/pve/node-maintenance.md)
- [RGW/S3 trả 503 hoặc timeout, upload lỗi](../cases/ceph/rgw-503.md)
- [VM treo IO do image RBD (watcher, lock, blocklist)](../cases/ceph/rbd-hang.md)
- [Thêm OSD hoặc node mới làm chậm production](../cases/ceph/add-osd-throttle.md)
- [Cluster đầy khẩn cấp: ghi bị chặn (OSD_FULL), backfill_toofull](../cases/ceph/cluster-full-emergency.md)
- [Latency OSD cao, IOPS thấp do SSD consumer (không có PLP)](../cases/ceph/osd-latency-consumer-ssd.md)
- [Nâng cấp Ceph trên Proxmox (ví dụ Reef lên Squid)](../cases/ceph/ceph-upgrade-pve.md)
- [Nâng cấp Proxmox VE 8 lên 9 trong cluster có Ceph](../cases/pve/pve-upgrade-8to9.md)
- [Một node chết hẳn (hỏng phần cứng): khôi phục dịch vụ](../cases/pve/node-dead-recovery.md)
- [Cờ bảo trì Ceph còn sót sau bảo trì (noout, noscrub, norecover...)](../cases/ceph/maintenance-flags-left.md)
- [Nâng cấp Ceph Quincy 17.2.8 → Reef 18.2.8 → Squid 19.2.4 trên PVE 8.4 (3 node, có CephFS)](../runbooks/rb-ceph-upgrade-quincy-reef-squid.md)
- [Bảo trì production: tắt HA và đặt cờ bảo trì Ceph trước khi tắt node](../runbooks/rb-prod-maintenance.md)
- [PVE host hỏng đĩa boot, không có backup cấu hình: kiểm kê và dựng lại node](../cases/pve/pve-host-rebuild-no-config-backup.md)
- [Xóa node Proxmox khỏi cluster an toàn (VM, HA và Ceph)](../runbooks/rb-pve-remove-node.md)
- [PG inconsistent / scrub errors](../cases/ceph/pg-inconsistent.md)
- [Ceph nearfull / full / pool đầy](../cases/ceph/nearfull-full.md)
- [OSD down hoặc up/down liên tục (flapping)](../cases/ceph/osd-down-flapping.md)
- [Clock skew trên MON (lệch giờ)](../cases/ceph/clock-skew.md)
- [PG degraded / undersized, recovery chậm](../cases/ceph/pg-degraded-recovery.md)
- [Large omap objects (thường do bucket index RGW)](../cases/ceph/large-omap.md)
- [Cảnh báo PG không được scrub / deep-scrub kịp thời](../cases/ceph/deep-scrub-late.md)
- [Cảnh báo too many / too few PGs, chỉnh pg_num](../cases/ceph/pg-count.md)
- [PG down, peering kẹt hoặc unfound objects (mất nhiều OSD)](../cases/ceph/pg-down-incomplete.md)
- [BLUEFS_SPILLOVER: metadata RocksDB tràn sang đĩa chậm](../cases/ceph/bluefs-spillover.md)
- [Storage dùng chung giữa hai cluster Proxmox gây xung đột lock/VMID](../cases/pve/pve-storage-shared-clusters.md)
