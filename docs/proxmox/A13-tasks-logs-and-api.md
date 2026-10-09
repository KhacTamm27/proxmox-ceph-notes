# A13 · Tasks, logs and API

[← Mục lục](../../README.md) · Proxmox host · 10 lệnh

[← A12 Access control (pveum)](../proxmox/A12-access-control-pveum.md) · [A14 Ceph management from Proxmox (pveceph) →](../proxmox/A14-ceph-management-from-proxmox-pveceph.md)

## Tasks

```bash
# Các tác vụ gần đây | Recent tasks
# từ khóa: task tác vụ lịch sử
pvenode task list

# Xem log của một tác vụ | Task log
# từ khóa: task log lỗi tác vụ
pvenode task log <upid>

# Trạng thái một tác vụ | Task state
# từ khóa: task trạng thái
pvenode task status <upid>
```

## Logs

```bash
# Theo dõi log daemon API | API daemon log
# từ khóa: log pvedaemon api
journalctl -u pvedaemon -f

# Theo dõi log web proxy | Web proxy log
# từ khóa: log pveproxy gui web đăng nhập
journalctl -u pveproxy -f

# Theo dõi syslog | System log
# từ khóa: syslog log hệ thống
tail -f /var/log/syslog
```

## API

```bash
# Trạng thái cluster qua API | Cluster status via API
# từ khóa: cluster trạng thái api
pvesh get /cluster/status

# Tất cả VM trong cluster | All VMs in cluster
# từ khóa: vm toàn cluster api
pvesh get /cluster/resources --type vm

# Trạng thái node qua API | Node status
# từ khóa: node trạng thái api
pvesh get /nodes/<node>/status

# Bật VM qua API | Start VM via API
# từ khóa: api start vm
pvesh create /nodes/<node>/qemu/<vmid>/status/start
```
