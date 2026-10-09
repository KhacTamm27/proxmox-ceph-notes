# A7 · High availability and replication

[← Mục lục](../../README.md) · Proxmox host · 14 lệnh

[← A6 Backup and restore](../proxmox/A06-backup-and-restore.md) · [A8 Network →](../proxmox/A08-network.md)

## Status

```bash
# Trạng thái CRM, LRM và từng tài nguyên HA | CRM, LRM and resource states
# từ khóa: ha trạng thái fence error freeze
ha-manager status

# Xem các tài nguyên HA đã cấu hình | Configured HA resources
# từ khóa: ha cấu hình
ha-manager config
```

## Resources

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

## Groups

```bash
# Tạo nhóm HA (PVE 8) | Create HA group (PVE 8)
# từ khóa: ha group nhóm ưu tiên node
ha-manager groupadd <group> --nodes node1:2,node2:1
```

## Move

```bash
# Live migrate VM đang trong HA | Live migrate an HA VM
# từ khóa: ha migrate
ha-manager migrate vm:<vmid> <node>

# Dừng, chuyển rồi bật lại VM HA | Stop, move, start
# từ khóa: ha relocate
ha-manager relocate vm:<vmid> <node>
```

## Maintenance

```bash
# Bật chế độ bảo trì node (PVE 8.2 trở lên) | Maintenance mode (PVE 8.2+)
# từ khóa: bảo trì maintenance node ha
ha-manager crm-command node-maintenance enable <node>

# Tắt chế độ bảo trì node | Leave maintenance mode
# từ khóa: kết thúc bảo trì maintenance
ha-manager crm-command node-maintenance disable <node>
```

## Services

```bash
# Trạng thái các daemon HA | HA daemons
# từ khóa: ha crm lrm service
systemctl status pve-ha-crm pve-ha-lrm
```

## Replication

```bash
# Liệt kê job replication | Replication jobs
# từ khóa: replication sao chép zfs job
pvesr list

# Trạng thái replication | Replication state
# từ khóa: replication lỗi trạng thái
pvesr status

# Tạo job replication ZFS | Create ZFS replication job
# từ khóa: tạo replication zfs lịch
pvesr create-local-job <vmid>-<n> <target-node> --schedule "*/15"
```
