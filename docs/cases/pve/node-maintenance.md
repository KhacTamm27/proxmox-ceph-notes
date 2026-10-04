# Bảo trì hoặc reboot một node Proxmox + Ceph

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** Cần reboot node để nâng cấp kernel hoặc thay phần cứng mà không làm gián đoạn VM và không kích hoạt rebalance.

**Nguyên nhân hay gặp:** Khi node tắt, OSD của nó down; sau 10 phút Ceph tự out và bắt đầu rebalance không cần thiết nếu không đặt noout.

## Các bước xử lý

1. Kiểm tra cluster đang khỏe trước khi bắt đầu

```bash
ceph -s
pvecm status
```

2. Đặt noout để Ceph không tự rebalance

```bash
ceph osd set noout
```

3. Di chuyển VM sang node khác

```bash
pvenode migrateall <target-node>
```

4. Reboot, đợi node và OSD lên lại

```bash
reboot
pvecm status
ceph osd stat
```

5. Khi các PG về active+clean thì gỡ noout

```bash
ceph -s
ceph osd unset noout
```

## Lưu ý

Mỗi lần chỉ làm một node. Đừng reboot node kế tiếp khi PG chưa active+clean. Quên unset noout là lỗi hay gặp: nếu sau đó một OSD chết thật, Ceph sẽ không tự phục hồi. Quy trình đầy đủ cho production (tắt HA, 6 cờ Ceph) xem runbook bảo trì production.

<!-- từ khóa: reboot bảo trì node maintenance noout migrate nâng cấp kernel -->
