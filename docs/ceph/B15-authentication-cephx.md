# B15 · Xác thực (cephx)

[← Mục lục](../../README.md) · Ceph · 6 lệnh · tên gốc: Authentication (cephx)

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← B14 CephFS](../ceph/B14-cephfs.md) · [B16 Benchmark và rados cấp thấp →](../ceph/B16-benchmarks-and-low-level-rados.md)

## Liệt kê (List)

```bash
# [chỉ đọc] Toàn bộ key và quyền | All keys and caps
# từ khóa: auth key quyền cephx
ceph auth ls
```

## Xem (Show)

```bash
# [chỉ đọc] Một key và quyền của nó | One key and caps
# từ khóa: auth key client
ceph auth get client.<name>

# [chỉ đọc] In ra secret của key | Print secret only
# từ khóa: secret key
ceph auth print-key client.<name>
```

## Tạo mới (Create)

```bash
# Tạo key cho client | Create client key
# từ khóa: tạo key client cephx
ceph auth get-or-create client.<name> mon 'allow r' osd 'allow rwx pool=<pool>'
```

## Thay đổi (Change)

```bash
# Đổi quyền của key | Change caps
# từ khóa: đổi quyền caps cephx
ceph auth caps client.<name> mon 'allow r' osd 'allow rw pool=<pool>'
```

## Xóa (Delete)

```bash
# ⚠ NGUY HIỂM: Xóa key (nguy hiểm) | Remove key (destructive)
# từ khóa: xóa key
ceph auth del client.<name>
```
