# B11 · Recovery, scrub and config tuning

[← Mục lục](../../README.md) · Ceph · 11 lệnh

[← B10 Placement groups](../ceph/B10-placement-groups.md) · [B12 RBD (VM disks) →](../ceph/B12-rbd-vm-disks.md)

## Config

```bash
# Toàn bộ cấu hình tập trung đã đặt | All centralized settings
# từ khóa: config cấu hình
ceph config dump

# Đọc một tùy chọn cấu hình | Read one option
# từ khóa: config get
ceph config get <who> <option>

# Đặt tùy chọn cấu hình | Set option
# từ khóa: config set
ceph config set <who> <option> <value>

# Đưa tùy chọn về mặc định | Reset option
# từ khóa: config reset
ceph config rm <who> <option>
```

## Backfill

```bash
# Giới hạn số backfill đồng thời để đỡ ảnh hưởng client | Limit concurrent backfills
# từ khóa: backfill chậm ảnh hưởng io throttle
ceph config set osd osd_max_backfills 1
```

## Recovery

```bash
# Giới hạn số thao tác recovery đồng thời | Limit recovery ops
# từ khóa: recovery throttle
ceph config set osd osd_recovery_max_active 1

# Làm chậm recovery trên SSD cho đỡ tải | Throttle recovery on SSD
# từ khóa: recovery ssd throttle
ceph config set osd osd_recovery_sleep_ssd 0.1
```

## mClock

```bash
# Ưu tiên IO của client hơn recovery (Quincy trở lên) | Favor client IO (Quincy and later)
# từ khóa: mclock ưu tiên client slow ops
ceph config set osd osd_mclock_profile high_client_ops

# Ưu tiên recovery hơn client (Quincy trở lên) | Favor recovery (Quincy and later)
# từ khóa: mclock ưu tiên recovery nhanh
ceph config set osd osd_mclock_profile high_recovery_ops
```

## Scrub

```bash
# Giờ bắt đầu cửa sổ scrub | Scrub window start
# từ khóa: scrub giờ cao điểm lịch
ceph config set osd osd_scrub_begin_hour 22

# Giờ kết thúc cửa sổ scrub | Scrub window end
# từ khóa: scrub giờ lịch
ceph config set osd osd_scrub_end_hour 6
```
