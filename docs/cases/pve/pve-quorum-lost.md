# Cluster Proxmox mất quorum

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** GUI báo "cluster not ready - no quorum", /etc/pve chuyển read-only, không start được VM, node hiện đỏ.

**Nguyên nhân hay gặp:** Mất liên lạc giữa các node (mạng, switch, firewall chặn UDP 5405-5412), quá nửa số node tắt, hoặc cluster 2 node thiếu QDevice.

## Các bước xử lý

1. Xem số phiếu và node nào đang thấy nhau

```bash
pvecm status
pvecm nodes
```

2. Kiểm tra link corosync giữa các node

```bash
corosync-cfgtool -s
journalctl -u corosync -f
```

3. Kiểm tra mạng: ping giữa các node qua mạng cluster, MTU, firewall

```bash
ping -M do -s 1472 <node-ip>
```

4. Khi mạng đã ổn, restart stack cluster

```bash
systemctl restart pve-cluster corosync
```

5. Khẩn cấp (chỉ khi chắc chắn các node kia đã tắt hẳn): ép quorum tạm thời

```bash
pvecm expected 1
```

## Lưu ý

pvecm expected 1 có nguy cơ split-brain nếu node kia thật ra vẫn chạy và ghi dữ liệu. Với cluster 2 node nên thêm QDevice. pmxcfs -l là biện pháp cuối cùng.

<!-- từ khóa: proxmox pve quorum mất quorum corosync cluster not ready read-only không start vm -->
