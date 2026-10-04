# Latency OSD cao, IOPS thấp do SSD consumer (không có PLP)

[← Mục lục](../../../README.md) · Case study Ceph

**Triệu chứng:** ceph osd perf cho commit/apply latency hàng chục đến hàng trăm ms ở một số OSD, VM chậm, thỉnh thoảng slow ops, benchmark cho IOPS rất thấp.

**Nguyên nhân hay gặp:** Ceph ghi đồng bộ (sync write). SSD consumer không có bảo vệ mất điện (PLP) không cache được ghi đồng bộ nên latency rất cao và tụt mạnh khi tải liên tục.

## Các bước xử lý

1. So sánh latency giữa các OSD, tìm OSD tệ nhất

```bash
ceph osd perf
```

2. Chạy benchmark ngắn trên OSD nghi ngờ (cẩn thận giờ cao điểm)

```bash
ceph tell osd.<osd-id> bench
```

3. Kiểm tra model đĩa và SMART

```bash
lsblk -d -o NAME,MODEL,SIZE
smartctl -a /dev/<dev>
```

4. Loại trừ nguyên nhân khác: mạng và recovery đang chạy

```bash
ethtool -S <if>
ceph -s
```

## Lưu ý

Cộng đồng Proxmox khuyến nghị SSD enterprise có PLP cho Ceph, giải pháp thật sự thường là thay đĩa. Đừng mua đĩa thay thế trước khi so sánh latency giữa các OSD cùng loại để chắc là đĩa chứ không phải mạng.

## Nguồn tham khảo

- [Proxmox forum: Ceph low performance](https://forum.proxmox.com/threads/ceph-low-performance.183462/)
- [Proxmox forum: High latency on Proxmox Ceph cluster](https://forum.proxmox.com/threads/high-latency-on-proxmox-ceph-cluster.181091/)

<!-- từ khóa: ceph latency cao iops thấp ssd consumer plp power loss protection nvme enterprise commit latency chậm vm -->
