# Node Proxmox đầy ổ root, dịch vụ lỗi

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** "No space left on device", dịch vụ không start, không ghi được /etc/pve, GUI lỗi.

**Nguyên nhân hay gặp:** Log (journal, ceph) phình to, backup hoặc ISO nằm trên local, file tạm.

## Các bước xử lý

1. Xem ổ nào đầy

```bash
df -h
df -i
```

2. Tìm thư mục chiếm nhiều nhất

```bash
du -xh / --max-depth=2 | sort -h | tail -20
```

3. Dọn log journal và cache apt

```bash
journalctl --disk-usage
journalctl --vacuum-size=500M
apt clean
```

4. Kiểm tra ổ chứa backup và ISO

```bash
pvesm status
du -sh /var/lib/vz/*
```

## Lưu ý

Không xóa tay trong /var/lib/ceph hay /etc/pve. Log Ceph lớn thì kiểm tra logrotate. Đặt cảnh báo khi ổ root vượt khoảng 80%.

<!-- từ khóa: proxmox đầy ổ root disk full log journal /var/log no space left on device -->
