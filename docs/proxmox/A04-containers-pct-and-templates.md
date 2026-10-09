# A4 · Containers (pct) and templates

[← Mục lục](../../README.md) · Proxmox host · 19 lệnh

[← A3 Virtual machines (qm)](../proxmox/A03-virtual-machines-qm.md) · [A5 Storage (pvesm) →](../proxmox/A05-storage-pvesm.md)

## Inspect

```bash
# Liệt kê container | List containers
# từ khóa: container lxc danh sách ct
pct list

# Trạng thái container | Status
# từ khóa: container trạng thái
pct status <ctid>

# Xem cấu hình container | Config
# từ khóa: container cấu hình lock
pct config <ctid>
```

## Power

```bash
# Bật, tắt êm, tắt cứng container | Power control
# từ khóa: bật tắt container start stop
pct start <ctid> / pct shutdown <ctid> / pct stop <ctid>
```

## Access

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

## Create

```bash
# Tạo container mới | Create container
# từ khóa: tạo container create
pct create <ctid> <template> --storage <storage>

# Clone container | Clone
# từ khóa: clone nhân bản container
pct clone <ctid> <newid>
```

## Config

```bash
# Đổi RAM và CPU của container | Change resources
# từ khóa: ram cpu container tài nguyên
pct set <ctid> --memory 2048 --cores 2

# Tăng dung lượng đĩa gốc container | Grow root disk
# từ khóa: mở rộng disk container đầy
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

## Migration

```bash
# Di chuyển container sang node khác | Migrate container
# từ khóa: migrate container
pct migrate <ctid> <node> --restart
```

## Delete

```bash
# ⚠ NGUY HIỂM: Xóa container (nguy hiểm) | Delete (destructive)
# từ khóa: xóa container destroy
pct destroy <ctid>
```

## Templates

```bash
# Cập nhật danh sách template | Refresh template list
# từ khóa: template cập nhật
pveam update

# Xem template có thể tải | Available templates
# từ khóa: template danh sách
pveam available

# Tải template về storage | Download template
# từ khóa: tải template download
pveam download <storage> <template>
```
