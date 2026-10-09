# Di chuyển VM giữa hai cluster Proxmox bằng remote migration

[← Mục lục](../../README.md) · Runbook

**Mục tiêu:** Di chuyển VM giữa hai cluster PVE độc lập bằng remote migration, kiểm soát quyền API, mapping network/storage và cutover.

**Điều kiện trước khi làm:** Xác nhận phiên bản PVE hai đầu hỗ trợ remote migration và mọi điều kiện của qm manual; có backup restore-point, quyền quản trị phù hợp, route/port cần thiết, mapping bridge/VLAN/storage và cửa sổ cutover. API token chỉ cấp quyền tối thiểu ở cluster đích; lưu secret ngoài shell history, ticket, chat và repo.

## Các bước

1. Kiểm kê VM, toàn bộ disk/snapshot/clone dependency, HA, bridge/VLAN và storage đích; kiểm tra cluster đích có đủ tài nguyên

```bash
qm config <source-vmid>
pvesm status
ha-manager status
```

2. Tạo và kiểm tra API token ở đích theo quyền tối thiểu; lấy fingerprint chứng chỉ đích qua kênh tin cậy và xác minh lại ngoài băng

```bash
pvenode cert info
```

3. Gỡ VM khỏi HA hoặc tạm dừng chính sách tự động theo change plan; chọn target VMID, bridge map, storage map và chế độ online/offline

4. Chạy qm remote-migrate theo cú pháp của đúng phiên bản PVE; truyền endpoint/token/fingerprint an toàn, không lưu lệnh chứa secret vào shell history hoặc tài liệu

```bash
qm remote-migrate <source-vmid> <target-vmid> '<destination-endpoint>' --target-bridge <bridge-map> --target-storage <storage-id> --online
```

5. Theo dõi task ở cả hai cluster; sau khi hoàn tất xác nhận VM đích, disk, boot, network, backup job và HA trước khi xóa VM nguồn theo change plan

```bash
qm status <target-vmid>
qm config <target-vmid>
pvesm status
```

## Lưu ý

Cú pháp chi tiết của `<destination-endpoint>` thay đổi theo CLI/version; xem qm manual trên đúng node trước khi chạy. `--online` không có nghĩa là application-consistent. Linked clone hoặc disk còn phụ thuộc base image có thể không được hỗ trợ trong một số version; không xóa base/unused disk để thử, hãy chuyển thành full clone theo quy trình được hỗ trợ và kiểm tra lại. Không dùng chung datastore/pool/LUN cho hai cluster ghi đồng thời; xem case storage dùng chung giữa hai cluster. Giữ nguồn và backup cho tới khi nghiệm thu; không chạy hai VM cùng identity/IP đồng thời.

## Nguồn tham khảo

- [Proxmox VE qm manual (remote-migrate)](https://pve.proxmox.com/pve-docs/qm.1.html)
- [Proxmox VE Admin Guide](https://pve.proxmox.com/pve-docs/pve-admin-guide.html)

<!-- từ khóa: proxmox pve remote-migrate remote migration live migrate di chuyển vm giữa 2 cluster cross cluster api token fingerprint linked clone target storage bridge -->
