# B1 · Health and status

[← Mục lục](../../README.md) · Ceph · 14 lệnh

[B2 MON →](../ceph/B02-mon.md)

## Overview

```bash
# Tổng quan sức khỏe cluster Ceph, lệnh đầu tiên cần chạy | Cluster summary
# từ khóa: status health tổng quan kiểm tra nhanh
ceph -s

# Xem sự kiện cluster chạy liên tục (recovery, scrub, lỗi) | Live event stream
# từ khóa: watch live theo dõi realtime
ceph -w
```

## Health

```bash
# Chi tiết từng cảnh báo HEALTH_WARN/ERR, cho biết PG/OSD/pool nào lỗi | Warnings with detail
# từ khóa: warn error cảnh báo lỗi health nearfull inconsistent large omap
ceph health detail

# Trạng thái cluster dạng JSON để đưa vào script | Machine-readable status
# từ khóa: json script monitoring
ceph status --format json-pretty
```

## Capacity

```bash
# Dung lượng thô và theo từng pool | Raw and per-pool usage
# từ khóa: đầy disk dung lượng usage capacity full
ceph df

# Dung lượng mở rộng kèm quota | Extended usage and quotas
# từ khóa: quota dung lượng pool
ceph df detail
```

## Versions

```bash
# Phiên bản các daemon, kiểm tra lệch version khi nâng cấp | Daemon versions
# từ khóa: version nâng cấp upgrade mixed
ceph versions

# Lấy ID của cluster | Cluster ID
# từ khóa: fsid cluster id
ceph fsid
```

## Log

```bash
# 50 dòng log cluster gần nhất | Recent cluster log
# từ khóa: log gần đây cluster log
ceph log last 50
```

## Crash

```bash
# Danh sách daemon đã crash (cảnh báo RECENT_CRASH) | Recorded daemon crashes
# từ khóa: crash daemon chết recent_crash
ceph crash ls

# Chi tiết một lần crash | Crash details
# từ khóa: crash backtrace
ceph crash info <crash-id>

# Xác nhận đã xem mọi crash để hết cảnh báo | Acknowledge crashes
# từ khóa: xóa cảnh báo crash archive
ceph crash archive-all
```

## Time

```bash
# Độ lệch giờ giữa các MON | MON clock skew
# từ khóa: clock skew lệch giờ mất đồng bộ giờ ntp
ceph time-sync-status
```

## Report

```bash
# Xuất báo cáo đầy đủ để gửi hỗ trợ hoặc phân tích | Full cluster report
# từ khóa: report báo cáo debug
ceph report
```
