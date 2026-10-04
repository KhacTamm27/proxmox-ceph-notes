# Nâng cấp Proxmox VE 8 lên 9 trong cluster có Ceph

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** Cần nâng cấp cluster Proxmox đang chạy production (có Ceph, HA) mà không gián đoạn dịch vụ.

**Nguyên nhân hay gặp:** Nâng cấp bản chính có thứ tự bắt buộc và phải làm từng node, nếu sai thứ tự có thể kẹt gói hoặc mất tính tương thích với Ceph.

## Các bước xử lý

1. Chạy bộ kiểm tra trước nâng cấp trên mọi node và sửa hết cảnh báo

```bash
pve8to9 --full
```

2. Lưu lại trạng thái trước khi làm (cluster, Ceph)

```bash
pvecm status
ceph -s
ceph osd tree
```

3. Đưa Ceph lên bản yêu cầu (Squid) trước, theo case nâng cấp Ceph

```bash
ceph versions
```

4. Từng node một: di chuyển VM đi, nâng cấp gói, reboot

```bash
pvenode migrateall <target-node>
apt update
apt full-upgrade
```

5. Sau mỗi node kiểm tra rồi mới làm node kế tiếp

```bash
pveversion -v
pvecm status
ceph -s
```

## Lưu ý

Làm theo trang hướng dẫn nâng cấp chính thức của Proxmox (có lưu ý riêng từng phiên bản), bài này chỉ là bộ khung kiểm tra. Nên có backup đầy đủ, và migrate VM từ node mới về node cũ chưa chắc được nên làm theo hướng cũ sang mới. Thực hiện ngoài giờ cao điểm.

## Nguồn tham khảo

- [Proxmox wiki: Ceph Reef to Squid](https://pve.proxmox.com/wiki/Ceph_Reef_to_Squid)
- [WZ-IT: Proxmox VE 8 to 9 upgrade guide](https://wz-it.com/en/blog/proxmox-ve-8-to-9-upgrade-guide-enterprise/)

<!-- từ khóa: proxmox nâng cấp upgrade pve 8 9 pve8to9 debian trixie ceph squid cluster full-upgrade reboot -->
