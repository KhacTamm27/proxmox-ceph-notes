# P2V Linux/Ubuntu: chuyển disk vật lý thành VM trên Proxmox

[← Mục lục](../../README.md) · Runbook

**Mục tiêu:** Tạo bản disk image nhất quán của máy Linux vật lý, import vào Proxmox VE và xác nhận VM mới boot/hoạt động trước khi dừng máy nguồn.

**Điều kiện trước khi làm:** Có backup đã thử khôi phục, VMID/storage đích và dung lượng tối thiểu bằng kích thước disk nguồn. Ưu tiên shutdown máy nguồn hoặc boot rescue để disk không bị ghi trong lúc copy; dừng/quiesce ứng dụng theo quy trình riêng.

## Các bước

1. Trên máy nguồn, xác định đúng whole-disk theo model/serial/WWN và bảo đảm filesystem không còn được ghi

```bash
lsblk -o NAME,SIZE,SERIAL,WWN,FSTYPE,MOUNTPOINTS
```

2. Copy raw image qua SSH vào đường dẫn có đủ dung lượng trên node PVE; dùng đường dẫn by-id đã xác nhận, không dùng ví dụ /dev/sda một cách máy móc

```bash
dd if=/dev/disk/by-id/<source-disk-id> bs=16M status=progress | ssh root@<pve-node> "cat > <destination-path>/<vmid>-disk.raw"
```

3. Tạo VM với BIOS/UEFI, CPU, RAM và NIC phù hợp nguồn; import raw disk vào storage đích

```bash
qm create <vmid> --name <vm-name> --memory <MiB> --cores <count> --net0 virtio,bridge=<bridge>
qm importdisk <vmid> <destination-path>/<vmid>-disk.raw <target-storage>
```

4. Trong Hardware của VM, gắn Unused Disk vào bus phù hợp, đặt thứ tự boot rồi thử khởi động trong network/VLAN cô lập

```bash
qm config <vmid>
qm status <vmid>
```

## Lưu ý

Lệnh `dd` đọc toàn bộ disk nên file raw có thể bằng dung lượng toàn ổ, kể cả vùng trống. Không chạy trên disk đang ghi nếu cần dữ liệu nhất quán (nhất là database); `dd` qua SSH bị ngắt thường để lại file dở dang và không tự resume. Kiểm tra destination path không trùng file cần giữ, quyền truy cập và dung lượng trước khi copy. Sau import, Proxmox có thể hiển thị disk là `Unused Disk`; gắn disk qua GUI hoặc theo đúng cấu hình VM đang dùng, không đoán volume ID. Giữ máy nguồn lại đến khi xác minh boot, dữ liệu, dịch vụ và network.

## Nguồn tham khảo

- [Proxmox VE qm manual (create/import disk)](https://pve.proxmox.com/pve-docs/qm.1.html)

<!-- từ khóa: p2v linux ubuntu physical to virtual chuyển máy vật lý sang vm dd raw ssh qm importdisk boot uefi bios migration -->
