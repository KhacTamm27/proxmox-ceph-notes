# A13 · Task, log và API

[← Mục lục](../../README.md) · Proxmox host · 10 lệnh · tên gốc: Tasks, logs and API

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← A12 Phân quyền (pveum)](../proxmox/A12-access-control-pveum.md) · [A14 Quản lý Ceph từ Proxmox (pveceph) →](../proxmox/A14-ceph-management-from-proxmox-pveceph.md)

## Task (Tasks)

```bash
# [chỉ đọc] Các tác vụ gần đây | Recent tasks
# từ khóa: task tác vụ lịch sử
pvenode task list

# [chỉ đọc] Xem log của một tác vụ | Task log
# từ khóa: task log lỗi tác vụ
pvenode task log <upid>

# [chỉ đọc] Trạng thái một tác vụ | Task state
# từ khóa: task trạng thái
pvenode task status <upid>
```

## Log (Logs)

```bash
# [chỉ đọc] Theo dõi log daemon API | API daemon log
# từ khóa: log pvedaemon api
journalctl -u pvedaemon -f

# [chỉ đọc] Theo dõi log web proxy | Web proxy log
# từ khóa: log pveproxy gui web đăng nhập
journalctl -u pveproxy -f

# [chỉ đọc] Theo dõi syslog | System log
# từ khóa: syslog log hệ thống
tail -f /var/log/syslog
```

## API

```bash
# [chỉ đọc] Trạng thái cluster qua API | Cluster status via API
# từ khóa: cluster trạng thái api
pvesh get /cluster/status

# [chỉ đọc] Tất cả VM trong cluster | All VMs in cluster
# từ khóa: vm toàn cluster api
pvesh get /cluster/resources --type vm

# [chỉ đọc] Trạng thái node qua API | Node status
# từ khóa: node trạng thái api
pvesh get /nodes/<node>/status

# Bật VM qua API | Start VM via API
# từ khóa: api start vm
pvesh create /nodes/<node>/qemu/<vmid>/status/start
```

## Case và runbook dùng lệnh trong nhóm này

- [PVE host hỏng đĩa boot, không có backup cấu hình: kiểm kê và dựng lại node](../cases/pve/pve-host-rebuild-no-config-backup.md)
- [Xóa node Proxmox khỏi cluster an toàn (VM, HA và Ceph)](../runbooks/rb-pve-remove-node.md)
- [Node dừng: HA khởi động lại đồng loạt VM làm tràn RAM (domino)](../cases/pve/ha-domino.md)
