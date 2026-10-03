# HA: VM không tự chạy lại trên node khác, trạng thái error hoặc fence

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** Node chết nhưng VM HA không tự khởi động ở node khác, hoặc VM HA ở trạng thái error, freeze, fence.

**Nguyên nhân hay gặp:** Mất quorum, storage không dùng chung, watchdog không hoạt động, VM từng start lỗi nên HA đặt về error.

## Các bước xử lý

1. Xem HA đang nghĩ gì về từng VM và node

```bash
ha-manager status
ha-manager config
```

2. Xem log của LRM và CRM

```bash
journalctl -u pve-ha-lrm -u pve-ha-crm --since "1 hour ago"
```

3. Cluster còn quorum không, storage có chung không

```bash
pvecm status
pvesm status
```

4. Khi đã xử lý nguyên nhân, đưa VM khỏi trạng thái error: disable rồi start lại

```bash
ha-manager set vm:<vmid> --state disabled
ha-manager set vm:<vmid> --state started
```

## Lưu ý

HA cần quorum và đĩa VM nằm trên storage dùng chung (Ceph). Fence và chuyển VM mất vài phút sau khi node mất liên lạc, không phải tức thì.

<!-- từ khóa: proxmox ha high availability fence error freeze node chết vm không tự chạy lại watchdog -->
