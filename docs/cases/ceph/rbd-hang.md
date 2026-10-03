# VM treo IO do image RBD (watcher, lock, blocklist)

[← Mục lục](../../../README.md) · Case study Ceph

**Triệu chứng:** VM đơ hoặc không start vì đĩa RBD, lỗi "image is locked", "timeout" khi mở image.

**Nguyên nhân hay gặp:** Client cũ (node đã chết) còn giữ lock hoặc watcher, client bị blocklist, hoặc pool đang chậm.

## Các bước xử lý

1. Cluster và pool có ổn không

```bash
ceph -s
ceph health detail
```

2. Ai đang watch và lock image

```bash
rbd status <pool>/<image>
rbd lock ls <pool>/<image>
```

3. Client có bị blocklist không

```bash
ceph osd blocklist ls
```

4. Nếu chủ lock là node đã chết hẳn thì chờ Ceph tự blocklist rồi start lại VM

```bash
qm start <vmid>
```

## Lưu ý

Chỉ xóa lock thủ công (rbd lock rm) khi chắc chắn client giữ lock đã chết, nếu không có nguy cơ hai nơi cùng ghi một image.

<!-- từ khóa: ceph rbd vm treo io lock watcher blocklist image không mở được -->
