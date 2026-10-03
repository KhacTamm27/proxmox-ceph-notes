# B5 · OSD flags and maintenance

[← Mục lục](../../README.md) · Ceph · 15 lệnh

[← B4 OSD status](../ceph/B04-osd-status.md) · [B6 OSD lifecycle and devices →](../ceph/B06-osd-lifecycle-and-devices.md)

## Flags

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

## Per subtree

```bash
# Đặt noout cho riêng một host hoặc chassis | Flag one CRUSH node
# từ khóa: bảo trì một host noout
ceph osd set-group noout <host-or-chassis>

# Gỡ noout của một host hoặc chassis | Clear flag on one CRUSH node
# từ khóa: xong bảo trì noout
ceph osd unset-group noout <host-or-chassis>
```

## Safety

```bash
# Kiểm tra dừng OSD này có mất tính sẵn sàng không | Safe to stop without losing availability
# từ khóa: dừng osd an toàn bảo trì
ceph osd ok-to-stop <osd-id>

# Kiểm tra xóa OSD này có mất dữ liệu không | Safe to destroy without data loss
# từ khóa: thay đĩa xóa osd an toàn
ceph osd safe-to-destroy <osd-id>
```

## State

```bash
# Đánh dấu OSD out để di dời dữ liệu, hoặc in để đưa lại | Mark out or in
# từ khóa: thay đĩa out in rebalance
ceph osd out <osd-id> / ceph osd in <osd-id>

# Đánh dấu OSD down (ép peering lại) | Mark down
# từ khóa: ép down osd
ceph osd down <osd-id>
```

## Weight

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
