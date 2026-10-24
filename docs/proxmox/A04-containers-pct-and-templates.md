# A4 · Container (pct) và template

[← Mục lục](../../README.md) · Proxmox host · 19 lệnh · tên gốc: Containers (pct) and templates

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← A3 Máy ảo (qm)](../proxmox/A03-virtual-machines-qm.md) · [A5 Storage (pvesm) →](../proxmox/A05-storage-pvesm.md)

## Xem thông tin (Inspect)

```bash
# [chỉ đọc] Liệt kê container | List containers
# từ khóa: container lxc danh sách ct
pct list

# [chỉ đọc] Trạng thái container | Status
# từ khóa: container trạng thái
pct status <ctid>

# [chỉ đọc] Xem cấu hình container | Config
# từ khóa: container cấu hình lock
pct config <ctid>
```

## Bật/tắt (Power)

```bash
# Bật, tắt êm, tắt cứng container | Power control
# từ khóa: bật tắt container start stop
pct start <ctid> / pct shutdown <ctid> / pct stop <ctid>
```

## Truy cập (Access)

```bash
# Vào shell bên trong container | Shell inside container
# từ khóa: vào container shell console
pct enter <ctid>

# Chạy lệnh trong container | Run command
# từ khóa: chạy lệnh container exec
pct exec <ctid> -- <cmd>

# Chép file vào container | Copy file in
# từ khóa: copy file vào container
pct push <ctid> <src> <dst>

# Chép file ra khỏi container | Copy file out
# từ khóa: copy file từ container
pct pull <ctid> <src> <dst>
```

## Tạo mới (Create)

```bash
# Tạo container mới | Create container
# từ khóa: tạo container create
pct create <ctid> <template> --storage <storage>

# Clone container | Clone
# từ khóa: clone nhân bản container
pct clone <ctid> <newid>
```

## Cấu hình (Config)

```bash
# Đổi RAM và CPU của container | Change resources
# từ khóa: ram cpu container tài nguyên
pct set <ctid> --memory 2048 --cores 2

# Tăng dung lượng đĩa gốc container | Grow root disk
# từ khóa: mở rộng disk container đầy tăng dung lượng ổ extend grow
pct resize <ctid> rootfs +5G

# Mở khóa container | Remove lock
# từ khóa: lock container backup
pct unlock <ctid>
```

## Snapshot

```bash
# Tạo snapshot và quay về snapshot container | Snapshot and roll back
# từ khóa: snapshot rollback container
pct snapshot <ctid> <name> / pct rollback <ctid> <name>
```

## Di chuyển (migrate) (Migration)

```bash
# Di chuyển container sang node khác | Migrate container
# từ khóa: migrate container
pct migrate <ctid> <node> --restart
```

## Xóa (Delete)

```bash
# ⚠ NGUY HIỂM: Xóa container (nguy hiểm) | Delete (destructive)
# từ khóa: xóa container destroy
pct destroy <ctid>
```

## Template (Templates)

```bash
# Cập nhật danh sách template | Refresh template list
# từ khóa: template cập nhật
pveam update

# [chỉ đọc] Xem template có thể tải | Available templates
# từ khóa: template danh sách
pveam available

# Tải template về storage | Download template
# từ khóa: tải template download
pveam download <storage> <template>
```

## Case và runbook dùng lệnh trong nhóm này

- [Cấu hình mạng Proxmox: OVS/Linux bridge, bond, LACP và VLAN trunk](../cases/pve/pve-network-bridge-bond-vlan.md)
