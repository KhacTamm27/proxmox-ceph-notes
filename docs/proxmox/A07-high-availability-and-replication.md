# A7 · HA và replication

[← Mục lục](../../README.md) · Proxmox host · 14 lệnh · tên gốc: High availability and replication

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← A6 Backup và khôi phục](../proxmox/A06-backup-and-restore.md) · [A8 Mạng →](../proxmox/A08-network.md)

## Trạng thái (Status)

```bash
# [chỉ đọc] Trạng thái CRM, LRM và từng tài nguyên HA | CRM, LRM and resource states
# từ khóa: ha trạng thái fence error freeze
ha-manager status

# [chỉ đọc] Xem các tài nguyên HA đã cấu hình | Configured HA resources
# từ khóa: ha cấu hình
ha-manager config
```

## Tài nguyên HA (Resources)

```bash
# Đưa VM vào HA | Add VM to HA
# từ khóa: thêm ha vm
ha-manager add vm:<vmid> --state started

# Đổi trạng thái HA của VM | Change HA state
# từ khóa: ha disabled started error reset
ha-manager set vm:<vmid> --state disabled

# Gỡ VM khỏi HA | Remove from HA
# từ khóa: gỡ ha remove
ha-manager remove vm:<vmid>
```

## Nhóm (Groups)

```bash
# Tạo nhóm HA (PVE 8) | Create HA group (PVE 8)
# từ khóa: ha group nhóm ưu tiên node
ha-manager groupadd <group> --nodes node1:2,node2:1
```

## Di chuyển (Move)

```bash
# Live migrate VM đang trong HA | Live migrate an HA VM
# từ khóa: ha migrate
ha-manager migrate vm:<vmid> <node>

# Dừng, chuyển rồi bật lại VM HA | Stop, move, start
# từ khóa: ha relocate
ha-manager relocate vm:<vmid> <node>
```

## Bảo trì (Maintenance)

```bash
# Bật chế độ bảo trì node (PVE 8.2 trở lên) | Maintenance mode (PVE 8.2+)
# từ khóa: bảo trì maintenance node ha
ha-manager crm-command node-maintenance enable <node>

# Tắt chế độ bảo trì node | Leave maintenance mode
# từ khóa: kết thúc bảo trì maintenance
ha-manager crm-command node-maintenance disable <node>
```

## Dịch vụ (Services)

```bash
# [chỉ đọc] Trạng thái các daemon HA | HA daemons
# từ khóa: ha crm lrm service
systemctl status pve-ha-crm pve-ha-lrm
```

## Replication

```bash
# [chỉ đọc] Liệt kê job replication | Replication jobs
# từ khóa: replication sao chép zfs job
pvesr list

# [chỉ đọc] Trạng thái replication | Replication state
# từ khóa: replication lỗi trạng thái
pvesr status

# Tạo job replication ZFS | Create ZFS replication job
# từ khóa: tạo replication zfs lịch
pvesr create-local-job <vmid>-<n> <target-node> --schedule "*/15"
```

## Case và runbook dùng lệnh trong nhóm này

- [HA: VM không tự chạy lại trên node khác, trạng thái error hoặc fence](../cases/pve/ha-no-restart.md)
- [Một node chết hẳn (hỏng phần cứng): khôi phục dịch vụ](../cases/pve/node-dead-recovery.md)
- [Node dừng: HA khởi động lại đồng loạt VM làm tràn RAM (domino)](../cases/pve/ha-domino.md)
- [Bảo trì production: tắt HA và đặt cờ bảo trì Ceph trước khi tắt node](../runbooks/rb-prod-maintenance.md)
- [PVE host hỏng đĩa boot, không có backup cấu hình: kiểm kê và dựng lại node](../cases/pve/pve-host-rebuild-no-config-backup.md)
- [Di chuyển VM giữa hai cluster Proxmox bằng remote migration](../runbooks/rb-pve-cross-cluster-migrate.md)
- [Xóa node Proxmox khỏi cluster an toàn (VM, HA và Ceph)](../runbooks/rb-pve-remove-node.md)
- [Proxmox ZFS replication: cấu hình và kiểm thử khôi phục VM](../runbooks/rb-pve-zfs-replication.md)
