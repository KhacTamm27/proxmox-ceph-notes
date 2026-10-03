# Migrate VM thất bại

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** Migrate báo lỗi, treo ở một phần trăm nào đó, hoặc không cho chọn node đích.

**Nguyên nhân hay gặp:** Đĩa nằm trên local storage, ISO local gắn vào VM, storage không có ở node đích, khác thế hệ CPU với CPU type host, VM đang bị lock, mạng migrate chậm.

## Các bước xử lý

1. Xem log lỗi của tác vụ migrate

```bash
pvesh get /nodes/<node>/tasks --limit 5
```

2. Kiểm tra cấu hình VM: đĩa local, cdrom, lock, passthrough

```bash
qm config <vmid>
```

3. Node đích có đủ storage cần thiết không

```bash
pvesm status
pvecm status
```

4. Thử lại (đĩa local thì thêm tùy chọn kèm đĩa)

```bash
qm migrate <vmid> <node> --online
qm migrate <vmid> <node> --online --with-local-disks
```

## Lưu ý

Gỡ ISO khỏi cdrom trước khi migrate. VM dùng CPU type host giữa các node khác thế hệ có thể lỗi, nên dùng CPU type chung nếu cần live migrate linh hoạt.

<!-- từ khóa: proxmox migrate vm thất bại live migration lỗi local disk cpu cdrom iso storage -->
