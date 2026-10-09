# A3 · Virtual machines (qm)

[← Mục lục](../../README.md) · Proxmox host · 39 lệnh

[← A2 Cluster and corosync](../proxmox/A02-cluster-and-corosync.md) · [A4 Containers (pct) and templates →](../proxmox/A04-containers-pct-and-templates.md)

## Inspect

```bash
# Liệt kê các VM trên node | List VMs on node
# từ khóa: danh sách vm máy ảo
qm list

# Trạng thái chi tiết của VM | Detailed VM status
# từ khóa: vm trạng thái ram cpu disk io
qm status <vmid> --verbose

# Xem cấu hình VM | VM config
# từ khóa: cấu hình vm lock đĩa network
qm config <vmid>

# Xem thay đổi cấu hình đang chờ áp dụng | Pending config changes
# từ khóa: pending chờ reboot thay đổi chưa áp dụng
qm pending <vmid>

# Xem dòng lệnh KVM sẽ chạy cho VM | Show KVM command line
# từ khóa: kvm qemu command line gỡ lỗi không start
qm showcmd <vmid> --pretty
```

## Power

```bash
# Bật VM | Start
# từ khóa: start bật khởi động vm lỗi không start
qm start <vmid>

# Tắt VM êm (gửi ACPI), chờ tối đa 60 giây | Clean shutdown
# từ khóa: tắt shutdown êm
qm shutdown <vmid> --timeout 60

# Tắt cứng VM | Hard stop
# từ khóa: stop tắt cứng vm treo kill
qm stop <vmid>

# Khởi động lại VM | Reboot
# từ khóa: reboot restart vm
qm reboot <vmid>

# Reset cứng VM | Hard reset
# từ khóa: reset treo
qm reset <vmid>

# Tạm dừng và tiếp tục VM | Suspend and resume
# từ khóa: suspend resume tạm dừng
qm suspend <vmid> / qm resume <vmid>
```

## Create

```bash
# Tạo VM mới | Create VM
# từ khóa: tạo vm mới create
qm create <vmid> --name <n> --memory 4096 --cores 2 --net0 virtio,bridge=vmbr0

# Clone VM đầy đủ (full clone) | Full clone
# từ khóa: clone nhân bản sao chép vm
qm clone <vmid> <newid> --full

# Chuyển VM thành template | Convert to template
# từ khóa: template mẫu
qm template <vmid>

# ⚠ NGUY HIỂM: Xóa VM (nguy hiểm) | Delete VM (destructive)
# từ khóa: xóa vm destroy delete purge
qm destroy <vmid> --purge
```

## Config

```bash
# Đổi RAM và số CPU của VM | Change CPU and RAM
# từ khóa: tăng ram cpu cấu hình resize
qm set <vmid> --memory 8192 --cores 4

# Thêm ổ đĩa cho VM | Add disk
# từ khóa: thêm đĩa disk mới
qm set <vmid> --scsi1 <storage>:<size-GiB>

# Tăng dung lượng đĩa VM | Grow disk
# từ khóa: mở rộng đĩa tăng disk resize hết dung lượng
qm resize <vmid> scsi0 +10G

# Chuyển đĩa VM sang storage khác | Move disk to another storage (alias `qm move-disk`)
# từ khóa: di chuyển đĩa move disk storage đầy
qm disk move <vmid> scsi0 <storage>

# Quét lại volume và sửa cấu hình | Rescan volumes and fix config
# từ khóa: rescan đĩa mồ côi unused disk sửa config
qm rescan

# Mở khóa VM đang bị lock | Remove stuck lock
# từ khóa: lock locked backup snapshot không start
qm unlock <vmid>
```

## Snapshot

```bash
# Tạo snapshot VM | Create snapshot
# từ khóa: snapshot chụp trạng thái
qm snapshot <vmid> <name>

# Liệt kê snapshot của VM | List snapshots
# từ khóa: snapshot danh sách
qm listsnapshot <vmid>

# Quay về snapshot | Roll back
# từ khóa: rollback khôi phục snapshot
qm rollback <vmid> <name>

# Xóa snapshot | Delete snapshot
# từ khóa: xóa snapshot giải phóng dung lượng thin đầy
qm delsnapshot <vmid> <name>
```

## Migration

```bash
# Live migration VM sang node khác | Live migration
# từ khóa: migrate di chuyển vm live online
qm migrate <vmid> <node> --online

# Live migration kèm đĩa local | Live migration with local disks
# từ khóa: migrate đĩa local không shared storage
qm migrate <vmid> <node> --online --with-local-disks
```

## Guest agent

```bash
# Kiểm tra guest agent có phản hồi | Check agent
# từ khóa: guest agent qemu-guest-agent backup freeze lỗi
qm agent <vmid> ping

# Chạy lệnh bên trong VM qua guest agent | Run command in guest
# từ khóa: chạy lệnh trong vm agent exec
qm guest exec <vmid> -- <cmd>

# Lấy IP của VM qua guest agent | Guest IPs
# từ khóa: ip vm địa chỉ agent
qm guest cmd <vmid> network-get-interfaces
```

## Console

```bash
# Mở console serial của VM | Serial console
# từ khóa: console serial terminal
qm terminal <vmid>

# Mở QEMU monitor | QEMU monitor
# từ khóa: qemu monitor gỡ lỗi
qm monitor <vmid>

# Gửi phím tắt tới VM | Send key
# từ khóa: gửi phím ctrl alt delete
qm sendkey <vmid> ctrl-alt-delete
```

## Cloud-init

```bash
# Xem user-data cloud-init được sinh ra | Show generated user-data
# từ khóa: cloud-init cloudinit user-data
qm cloudinit dump <vmid> user

# Đặt thông số cloud-init (user, SSH key, IP) | Set cloud-init values
# từ khóa: cloud-init ssh key ip user
qm set <vmid> --ciuser <u> --sshkeys <file> --ipconfig0 ip=dhcp
```

## Import

```bash
# Thêm nguồn import từ ESXi (PVE 8.2 trở lên) | Add ESXi import source (PVE 8.2+)
# từ khóa: esxi vmware import chuyển từ vmware
pvesm add esxi <id> --server <host> --username <u> --password <p>

# Import VM từ file OVF | Import OVF
# từ khóa: import ovf vmware chuyển vm
qm importovf <vmid> <file.ovf> <storage>

# Import file đĩa vào VM | Import disk image
# từ khóa: import đĩa vmdk qcow2 raw
qm importdisk <vmid> <disk-file> <storage>

# Chuyển đổi đĩa VMware sang raw | Convert VMware disk
# từ khóa: convert vmdk raw chuyển đổi định dạng đĩa
qemu-img convert -f vmdk -O raw <src.vmdk> <dst.raw>
```
