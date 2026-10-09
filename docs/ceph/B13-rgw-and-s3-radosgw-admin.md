# B13 · RGW and S3 (radosgw-admin)

[← Mục lục](../../README.md) · Ceph · 33 lệnh

[← B12 RBD (VM disks)](../ceph/B12-rbd-vm-disks.md) · [B14 CephFS →](../ceph/B14-cephfs.md)

## Service

```bash
# Trạng thái daemon RGW | RGW daemon state
# từ khóa: rgw service s3 503 treo
systemctl status ceph-radosgw@rgw.<name>
```

## Users

```bash
# Liệt kê user S3 | List users
# từ khóa: user s3 danh sách
radosgw-admin user list

# Chi tiết user và key | User detail and keys
# từ khóa: user key suspended quota 403
radosgw-admin user info --uid=<uid>

# Tạo user S3 | Create user
# từ khóa: tạo user s3
radosgw-admin user create --uid=<uid> --display-name=<name>

# Sửa thông số user | Change user
# từ khóa: sửa user max bucket
radosgw-admin user modify --uid=<uid> --max-buckets=<n>

# Khóa hoặc mở lại user | Suspend or enable
# từ khóa: suspend khóa user 403
radosgw-admin user suspend --uid=<uid> / radosgw-admin user enable --uid=<uid>

# ⚠ NGUY HIỂM: Xóa user và dữ liệu (nguy hiểm) | Delete user and data (destructive)
# từ khóa: xóa user purge
radosgw-admin user rm --uid=<uid> --purge-data
```

## Keys

```bash
# Tạo key S3 mới | New S3 key
# từ khóa: key access secret tạo key
radosgw-admin key create --uid=<uid> --key-type=s3 --gen-access-key --gen-secret

# Xóa key | Remove key
# từ khóa: xóa key
radosgw-admin key rm --uid=<uid> --access-key=<key>
```

## Subuser

```bash
# Tạo subuser | Create subuser
# từ khóa: subuser
radosgw-admin subuser create --uid=<uid> --subuser=<uid>:<sub> --access=full
```

## Quota

```bash
# Đặt quota cho user | Set user quota
# từ khóa: quota user vượt quota 403
radosgw-admin quota set --quota-scope=user --uid=<uid> --max-size=<bytes> --max-objects=<n>

# Đặt quota cho bucket | Set bucket quota
# từ khóa: quota bucket
radosgw-admin quota set --quota-scope=bucket --uid=<uid> --max-size=<bytes>

# Bật quota | Enable quota
# từ khóa: bật quota
radosgw-admin quota enable --quota-scope=user --uid=<uid>
```

## Buckets

```bash
# Liệt kê bucket | List buckets
# từ khóa: bucket danh sách
radosgw-admin bucket list

# Bucket của một user | Buckets of a user
# từ khóa: bucket user
radosgw-admin bucket list --uid=<uid>

# Dung lượng, số object, số shard của bucket | Bucket size, objects, shards
# từ khóa: bucket dung lượng quota shard
radosgw-admin bucket stats --bucket=<bucket>

# Bucket vượt giới hạn shard (nguyên nhân large omap) | Objects per shard and fill status
# từ khóa: large omap shard bucket index rgw
radosgw-admin bucket limit check

# Kiểm tra index của bucket | Index check
# từ khóa: bucket index kiểm tra
radosgw-admin bucket check --bucket=<bucket>

# ⚠ NGUY HIỂM: Xóa bucket (nguy hiểm) | Delete bucket (destructive)
# từ khóa: xóa bucket
radosgw-admin bucket rm --bucket=<bucket> --purge-objects
```

## Reshard

```bash
# Các reshard đang chờ | Queued reshards
# từ khóa: reshard hàng đợi
radosgw-admin reshard list

# Trạng thái reshard của bucket | Reshard state
# từ khóa: reshard trạng thái
radosgw-admin reshard status --bucket=<bucket>

# Reshard index của bucket | Reshard bucket index
# từ khóa: reshard large omap shard
radosgw-admin bucket reshard --bucket=<bucket> --num-shards=<n>
```

## Usage

```bash
# Xem log sử dụng | Usage log
# từ khóa: usage băng thông thống kê
radosgw-admin usage show --uid=<uid>
```

## Lifecycle

```bash
# Trạng thái lifecycle | Lifecycle status
# từ khóa: lifecycle vòng đời xóa tự động
radosgw-admin lc list

# Chạy lifecycle ngay | Run lifecycle now
# từ khóa: lifecycle chạy ngay
radosgw-admin lc process
```

## GC

```bash
# Rác đang chờ dọn | Pending garbage
# từ khóa: gc rác dung lượng không giảm
radosgw-admin gc list --include-all

# Chạy dọn rác ngay | Run GC now
# từ khóa: gc dọn rác giải phóng dung lượng
radosgw-admin gc process
```

## Topology

```bash
# Cấu hình zone | Zone config
# từ khóa: zone multisite
radosgw-admin zone get

# Cấu hình zonegroup | Zonegroup config
# từ khóa: zonegroup multisite
radosgw-admin zonegroup get

# Liệt kê realm | Realms
# từ khóa: realm multisite
radosgw-admin realm list

# Period hiện tại | Current period
# từ khóa: period multisite
radosgw-admin period get

# Trạng thái đồng bộ multisite | Multisite sync state
# từ khóa: sync multisite đồng bộ chậm
radosgw-admin sync status
```

## Index pool

```bash
# Các key trong object index (kiểm tra large omap) | Keys in an index object (large omap check)
# từ khóa: large omap index bucket
rados -p <index-pool> listomapkeys <object>
```
