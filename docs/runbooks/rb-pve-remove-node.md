# Xóa node Proxmox khỏi cluster an toàn (VM, HA và Ceph)

[← Mục lục](../../README.md) · Runbook

**Mục tiêu:** Gỡ một node PVE khỏi cluster sau khi đã xử lý workload, HA và mọi dịch vụ Ceph gắn với node đó.

**Điều kiện trước khi làm:** Có quorum ổn định, backup mới và change plan được duyệt. Phân biệt node đang hoạt động với node đã chết; cách gỡ Ceph OSD/MON/MGR/MDS phụ thuộc vai trò và tình trạng dữ liệu. Không dùng checklist này để xóa node chỉ nhằm xử lý lỗi tạm thời.

## Các bước

1. Kiểm tra membership/quorum, workload, HA, Ceph và storage trước khi thay đổi

```bash
pvecm status
pvecm nodes
pvesh get /cluster/resources --type vm
ha-manager status
ceph -s
ceph osd tree
ceph mon dump
ceph mgr dump
ceph fs status
```

2. Migrate/backup toàn bộ VM/CT và gỡ chúng khỏi HA/backup/monitoring theo kế hoạch; xác nhận target chạy ổn trước khi tiếp tục

3. Nếu node có OSD, MON, MGR hoặc MDS, gỡ từng service bằng quy trình Ceph chính thức phù hợp; xác nhận cluster còn HEALTH_OK/đủ replica/quorum theo thiết kế

```bash
ceph -s
ceph osd tree
ceph fs status
```

4. Shutdown node cần xóa; từ node còn lại chạy delnode sau khi xác nhận đúng hostname và dịch vụ đã được xử lý

```bash
pvecm delnode <node-name>
```

5. Xác minh membership và storage sau khi gỡ; chỉ dọn cấu hình node ma còn sót theo case ghost-node-rejoin khi membership đã xác nhận node không còn

```bash
pvecm status
pvecm nodes
ceph -s
pvesm status
```

## Lưu ý

`pvecm delnode` chỉ sửa membership PVE; nó không tự migrate VM, remove OSD/MON/MGR/MDS, xóa dữ liệu Ceph hay thu hồi quyền truy cập shared storage. Không chạy `rm -rf /etc/pve/nodes/...` như bước mặc định. Nếu node mất liên lạc nhưng có thể vẫn ghi dữ liệu, fence/power-off xác nhận trước mọi thao tác có nguy cơ khởi chạy VM ở nơi khác. Khi thay node hoặc join lại cùng tên, xem [case PVE host hỏng](../cases/pve/pve-host-rebuild-no-config-backup.md) và [case node ma sau khi gỡ](../cases/pve/ghost-node-rejoin.md).

## Nguồn tham khảo

- [Proxmox VE Admin Guide](https://pve.proxmox.com/pve-docs/pve-admin-guide.html)

<!-- từ khóa: proxmox pve remove node xóa node pvecm delnode cluster ceph osd mon mgr mds migrate workload -->
