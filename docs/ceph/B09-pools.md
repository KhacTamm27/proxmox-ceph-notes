# B9 · Pool

[← Mục lục](../../README.md) · Ceph · 18 lệnh · tên gốc: Pools

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← B8 CRUSH map](../ceph/B08-crush-map.md) · [B10 Placement group (PG) →](../ceph/B10-placement-groups.md)

## Xem (View)

```bash
# [chỉ đọc] Pool kèm các thiết lập | Pools with settings
# từ khóa: pool danh sách chi tiết size min_size
ceph osd pool ls detail

# [chỉ đọc] Toàn bộ thiết lập của pool | All settings of a pool
# từ khóa: pool cấu hình
ceph osd pool get <pool> all

# [chỉ đọc] IO client và recovery theo pool | Client and recovery IO per pool
# từ khóa: pool io recovery
ceph osd pool stats
```

## Tạo mới (Create)

```bash
# Tạo pool | Create pool
# từ khóa: tạo pool
ceph osd pool create <pool> <pg_num>

# Gắn nhãn ứng dụng cho pool | Tag pool application
# từ khóa: pool_app_not_enabled cảnh báo application
ceph osd pool application enable <pool> rbd
```

## Thiết lập (Settings)

```bash
# Số bản sao của pool | Replica count
# từ khóa: size replica bản sao
ceph osd pool set <pool> size 3

# Số bản sao tối thiểu để cho phép IO | Minimum replicas for IO
# từ khóa: min_size pg inactive io treo
ceph osd pool set <pool> min_size 2

# Đổi rule đặt dữ liệu của pool | Change placement rule
# từ khóa: crush rule pool
ceph osd pool set <pool> crush_rule <rule>

# Bật tự động chỉnh số PG | Autoscaler
# từ khóa: autoscale pg too many
ceph osd pool set <pool> pg_autoscale_mode on

# Tỉ lệ dung lượng dự kiến của pool | Expected share of capacity
# từ khóa: target size ratio autoscale
ceph osd pool set <pool> target_size_ratio 0.9

# Chống xóa nhầm pool | Protect from deletion
# từ khóa: bảo vệ pool nodelete
ceph osd pool set <pool> nodelete true
```

## Tự co giãn PG (Autoscale)

```bash
# [chỉ đọc] Xem autoscaler đề xuất PG | PG autoscaler view
# từ khóa: autoscale pg số pg
ceph osd pool autoscale-status
```

## Hạn mức (quota) (Quota)

```bash
# Đặt quota cho pool | Set quota
# từ khóa: quota pool giới hạn
ceph osd pool set-quota <pool> max_bytes <n>

# [chỉ đọc] Xem quota của pool | Show quota
# từ khóa: quota pool
ceph osd pool get-quota <pool>
```

## Đổi tên (Rename)

```bash
# Đổi tên pool | Rename pool
# từ khóa: đổi tên pool
ceph osd pool rename <old> <new>
```

## Xóa (Delete)

```bash
# Cho phép xóa pool | Allow deletion
# từ khóa: cho phép xóa pool
ceph config set mon mon_allow_pool_delete true

# ⚠ NGUY HIỂM: Xóa pool (nguy hiểm) | Delete pool (destructive)
# từ khóa: xóa pool delete
ceph osd pool delete <pool> <pool> --yes-i-really-really-mean-it
```

## Mức sử dụng (Usage)

```bash
# [chỉ đọc] Số object và dung lượng theo pool | Objects and bytes per pool
# từ khóa: dung lượng pool object
rados df
```

## Case và runbook dùng lệnh trong nhóm này

- [Storage dùng chung giữa hai cluster Proxmox gây xung đột lock/VMID](../cases/pve/pve-storage-shared-clusters.md)
- [Cảnh báo too many / too few PGs, chỉnh pg_num](../cases/ceph/pg-count.md)
