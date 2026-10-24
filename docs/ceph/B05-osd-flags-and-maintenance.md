# B5 · Cờ OSD và bảo trì

[← Mục lục](../../README.md) · Ceph · 15 lệnh · tên gốc: OSD flags and maintenance

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← B4 Trạng thái OSD](../ceph/B04-osd-status.md) · [B6 Vòng đời OSD và thiết bị →](../ceph/B06-osd-lifecycle-and-devices.md)

## Cờ (Flags)

```bash
# Không tự đánh dấu OSD out (bật trước khi bảo trì, nhớ tắt sau) | Do not mark OSDs out
# từ khóa: bảo trì reboot maintenance noout
ceph osd set noout / ceph osd unset noout

# Tạm dừng cân bằng lại dữ liệu | Pause rebalancing
# từ khóa: rebalance tạm dừng
ceph osd set norebalance / ceph osd unset norebalance

# Tạm dừng backfill | Pause backfill
# từ khóa: backfill tạm dừng
ceph osd set nobackfill / ceph osd unset nobackfill

# Tạm dừng recovery | Pause recovery
# từ khóa: recovery tạm dừng
ceph osd set norecover / ceph osd unset norecover

# Tạm dừng scrub và deep-scrub (giờ cao điểm) | Pause scrubs
# từ khóa: scrub dừng cao điểm chậm
ceph osd set noscrub / ceph osd set nodeep-scrub

# Dừng toàn bộ IO của client (khẩn cấp) | Pause all client IO (emergency)
# từ khóa: pause dừng io khẩn cấp
ceph osd set pause / ceph osd unset pause
```

## Theo nhánh (subtree) (Per subtree)

```bash
# Đặt noout cho riêng một host hoặc chassis | Flag one CRUSH node
# từ khóa: bảo trì một host noout
ceph osd set-group noout <host-or-chassis>

# Gỡ noout của một host hoặc chassis | Clear flag on one CRUSH node
# từ khóa: xong bảo trì noout
ceph osd unset-group noout <host-or-chassis>
```

## Kiểm tra an toàn (Safety)

```bash
# [chỉ đọc] Kiểm tra dừng OSD này có mất tính sẵn sàng không | Safe to stop without losing availability
# từ khóa: dừng osd an toàn bảo trì
ceph osd ok-to-stop <osd-id>

# [chỉ đọc] Kiểm tra xóa OSD này có mất dữ liệu không | Safe to destroy without data loss
# từ khóa: thay đĩa xóa osd an toàn
ceph osd safe-to-destroy <osd-id>
```

## Trạng thái (State)

```bash
# Đánh dấu OSD out để di dời dữ liệu, hoặc in để đưa lại | Mark out or in
# từ khóa: thay đĩa out in rebalance
ceph osd out <osd-id> / ceph osd in <osd-id>

# Đánh dấu OSD down (ép peering lại) | Mark down
# từ khóa: ép down osd
ceph osd down <osd-id>
```

## Trọng số (Weight)

```bash
# Giảm tạm trọng số OSD (0 đến 1) | Temporary weight (0 to 1)
# từ khóa: osd đầy giảm tải reweight
ceph osd reweight <osd-id> 0.9

# Đổi trọng số CRUSH của OSD (thường theo dung lượng đĩa) | CRUSH weight
# từ khóa: crush weight đĩa mới
ceph osd crush reweight osd.<id> <weight>

# Tự giảm trọng số các OSD đang quá đầy | Auto reweight overfull OSDs
# từ khóa: nearfull cân bằng tự động
ceph osd reweight-by-utilization
```

## Case và runbook dùng lệnh trong nhóm này

- [OSD down hoặc up/down liên tục (flapping)](../cases/ceph/osd-down-flapping.md)
- [Bảo trì hoặc reboot một node Proxmox + Ceph](../cases/pve/node-maintenance.md)
- [Nâng cấp Ceph trên Proxmox (ví dụ Reef lên Squid)](../cases/ceph/ceph-upgrade-pve.md)
- [Một node chết hẳn (hỏng phần cứng): khôi phục dịch vụ](../cases/pve/node-dead-recovery.md)
- [Cờ bảo trì Ceph còn sót sau bảo trì (noout, noscrub, norecover...)](../cases/ceph/maintenance-flags-left.md)
- [Nâng cấp Ceph Quincy 17.2.8 → Reef 18.2.8 → Squid 19.2.4 trên PVE 8.4 (3 node, có CephFS)](../runbooks/rb-ceph-upgrade-quincy-reef-squid.md)
- [Bảo trì production: tắt HA và đặt cờ bảo trì Ceph trước khi tắt node](../runbooks/rb-prod-maintenance.md)
- [Thêm OSD hoặc node mới làm chậm production](../cases/ceph/add-osd-throttle.md)
- [Slow ops / blocked requests (Ceph chậm, IO bị chặn)](../cases/ceph/slow-ops.md)
- [Thay đĩa OSD hỏng](../cases/ceph/osd-replace-disk.md)
- [Ceph cảnh báo OSD device có nguy cơ hỏng](../cases/ceph/osd-device-health-warning.md)
- [Ceph nearfull / full / pool đầy](../cases/ceph/nearfull-full.md)
- [Cluster đầy khẩn cấp: ghi bị chặn (OSD_FULL), backfill_toofull](../cases/ceph/cluster-full-emergency.md)
