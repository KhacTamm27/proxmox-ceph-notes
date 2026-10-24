# B17 · Nâng cấp và tương thích

[← Mục lục](../../README.md) · Ceph · 8 lệnh · tên gốc: Upgrade and compatibility

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← B16 Benchmark và rados cấp thấp](../ceph/B16-benchmarks-and-low-level-rados.md) · [B18 Xử lý sự cố nhanh →](../ceph/B18-troubleshooting-shortlist.md)

## Phiên bản (Versions)

```bash
# [chỉ đọc] Phiên bản các daemon, kiểm tra lệch version khi nâng cấp | Mixed-version check
# từ khóa: version nâng cấp upgrade mixed
ceph versions
```

## Phiên bản (Release)

```bash
# [chỉ đọc] OSD map: flag, ratio, thông tin pool | Read `require_osd_release` and flags
# từ khóa: flags noout full ratio pool
ceph osd dump

# Chốt phiên bản OSD sau nâng cấp | Finalize OSD release after upgrade
# từ khóa: nâng cấp upgrade require-osd-release cảnh báo
ceph osd require-osd-release <release>
```

## Client (Clients)

```bash
# Phiên bản client tối thiểu (cần cho upmap) | Minimum client version (needed for upmap)
# từ khóa: compat client upmap balancer
ceph osd set-require-min-compat-client <release>

# [chỉ đọc] Mức tính năng của các client đang kết nối | Connected client feature levels
# từ khóa: client feature phiên bản cũ
ceph features
```

## Trước nâng cấp (Pre-upgrade)

```bash
# Tránh rebalance khi restart lần lượt | Avoid rebalance during rolling restart
# từ khóa: noout bảo trì nâng cấp
ceph osd set noout

# [chỉ đọc] Tổng quan sức khỏe cluster Ceph, lệnh đầu tiên cần chạy | Confirm all PGs `active+clean` before next node
# từ khóa: status health tổng quan kiểm tra nhanh
ceph -s
```

## Sau nâng cấp (Post-upgrade)

```bash
# Trả về hoạt động bình thường | Restore normal behavior
# từ khóa: gỡ noout xong bảo trì
ceph osd unset noout
```

## Case và runbook dùng lệnh trong nhóm này

- [Nâng cấp Ceph trên Proxmox (ví dụ Reef lên Squid)](../cases/ceph/ceph-upgrade-pve.md)
- [Nâng cấp Ceph Quincy 17.2.8 → Reef 18.2.8 → Squid 19.2.4 trên PVE 8.4 (3 node, có CephFS)](../runbooks/rb-ceph-upgrade-quincy-reef-squid.md)
