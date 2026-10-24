# A3 · Máy ảo (qm)

[← Mục lục](../../README.md) · Proxmox host · 39 lệnh · tên gốc: Virtual machines (qm)

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← A2 Cluster và corosync](../proxmox/A02-cluster-and-corosync.md) · [A4 Container (pct) và template →](../proxmox/A04-containers-pct-and-templates.md)

## Xem thông tin (Inspect)

```bash
# [chỉ đọc] Liệt kê các VM trên node | List VMs on node
# từ khóa: danh sách vm máy ảo vmid liệt kê
qm list

# [chỉ đọc] Trạng thái chi tiết của VM | Detailed VM status
# từ khóa: vm trạng thái ram cpu disk io
qm status <vmid> --verbose

# [chỉ đọc] Xem cấu hình VM | VM config
# từ khóa: cấu hình vm lock đĩa network
qm config <vmid>

# [chỉ đọc] Xem thay đổi cấu hình đang chờ áp dụng | Pending config changes
# từ khóa: pending chờ reboot thay đổi chưa áp dụng
qm pending <vmid>

# [chỉ đọc] Xem dòng lệnh KVM sẽ chạy cho VM | Show KVM command line
# từ khóa: kvm qemu command line gỡ lỗi không start
qm showcmd <vmid> --pretty
```

## Bật/tắt (Power)

```bash
# Bật VM | Start
# từ khóa: start bật khởi động vm lỗi không start
qm start <vmid>

# Tắt VM êm (gửi ACPI), chờ tối đa 60 giây | Clean shutdown
# từ khóa: tắt shutdown êm
qm shutdown <vmid> --timeout 60

# Tắt cứng VM | Hard stop
# từ khóa: stop tắt cứng vm treo kill force ngang
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

## Tạo mới (Create)

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

## Cấu hình (Config)

```bash
# Đổi RAM và số CPU của VM | Change CPU and RAM
# từ khóa: tăng ram cpu cấu hình resize
qm set <vmid> --memory 8192 --cores 4

# Thêm ổ đĩa cho VM | Add disk
# từ khóa: thêm đĩa disk mới
qm set <vmid> --scsi1 <storage>:<size-GiB>

# Tăng dung lượng đĩa VM | Grow disk
# từ khóa: mở rộng đĩa tăng disk resize hết dung lượng ổ vm extend grow
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

# [chỉ đọc] Liệt kê snapshot của VM | List snapshots
# từ khóa: snapshot danh sách
qm listsnapshot <vmid>

# Quay về snapshot | Roll back
# từ khóa: rollback khôi phục snapshot
qm rollback <vmid> <name>

# Xóa snapshot | Delete snapshot
# từ khóa: xóa snapshot giải phóng dung lượng thin đầy
qm delsnapshot <vmid> <name>
```

## Di chuyển (migrate) (Migration)

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
# [chỉ đọc] Kiểm tra guest agent có phản hồi | Check agent
# từ khóa: guest agent qemu-guest-agent backup freeze lỗi
qm agent <vmid> ping

# Chạy lệnh bên trong VM qua guest agent | Run command in guest
# từ khóa: chạy lệnh trong vm agent exec
qm guest exec <vmid> -- <cmd>

# [chỉ đọc] Lấy IP của VM qua guest agent | Guest IPs
# từ khóa: ip vm địa chỉ agent tìm của mac address interface
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
# [chỉ đọc] Xem user-data cloud-init được sinh ra | Show generated user-data
# từ khóa: cloud-init cloudinit user-data
qm cloudinit dump <vmid> user

# Đặt thông số cloud-init (user, SSH key, IP) | Set cloud-init values
# từ khóa: cloud-init ssh key ip user
qm set <vmid> --ciuser <u> --sshkeys <file> --ipconfig0 ip=dhcp
```

## Nhập (import) (Import)

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

## Case và runbook dùng lệnh trong nhóm này

- [VM bị lock (backup/snapshot), không start hoặc migrate được](../cases/pve/vm-locked.md)
- [Console VM qua proxy không kết nối (màn hình đen, 401, 403, 404, 502, WebSocket đứt)](../cases/pve/console-proxy-fail.md)
- [Proxmox ZFS replication: cấu hình và kiểm thử khôi phục VM](../runbooks/rb-pve-zfs-replication.md)
- [P2V Linux/Ubuntu: chuyển disk vật lý thành VM trên Proxmox](../runbooks/rb-p2v-linux.md)
- [P2V Windows: Disk2vhd, import VHDX và cài driver Proxmox](../runbooks/rb-p2v-windows.md)
- [V2V Hyper-V sang Proxmox bằng StarWind V2V Converter](../runbooks/rb-v2v-hyperv.md)
- [V2V VMware ESXi sang Proxmox bằng StarWind V2V Converter](../runbooks/rb-v2v-esxi.md)
- [Storage dùng chung giữa hai cluster Proxmox gây xung đột lock/VMID](../cases/pve/pve-storage-shared-clusters.md)
- [Cấu hình mạng Proxmox: OVS/Linux bridge, bond, LACP và VLAN trunk](../cases/pve/pve-network-bridge-bond-vlan.md)
- [Migrate VM thất bại](../cases/pve/migrate-fail.md)
- [VM không start được](../cases/pve/vm-wont-start.md)
- [Di chuyển VM giữa hai cluster Proxmox bằng remote migration](../runbooks/rb-pve-cross-cluster-migrate.md)
- [VM treo IO do image RBD (watcher, lock, blocklist)](../cases/ceph/rbd-hang.md)
- [Một node chết hẳn (hỏng phần cứng): khôi phục dịch vụ](../cases/pve/node-dead-recovery.md)
- [Backup vzdump lỗi hoặc treo](../cases/pve/backup-fail.md)
- [local-lvm (thin pool) đầy](../cases/pve/lvm-thin-full.md)
