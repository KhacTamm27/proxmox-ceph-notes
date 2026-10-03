# Mạng Ceph: MTU không khớp, nghẽn hoặc rớt gói

[← Mục lục](../../../README.md) · Case study Ceph

**Triệu chứng:** Slow ops hoặc OSD flapping chỉ liên quan một vài node, ping thường được nhưng IO lớn bị treo.

**Nguyên nhân hay gặp:** MTU 9000 cấu hình không đồng nhất trên NIC, bridge, bond và switch; cổng switch lỗi; bond hash không đều.

## Các bước xử lý

1. Kiểm tra MTU thực sự thông suốt giữa hai node (jumbo 9000 thì dùng 8972)

```bash
ping -M do -s 8972 <peer-ip>
```

2. Xem MTU và lỗi trên interface

```bash
ip -s link show <if>
ethtool -S <if>
```

3. Đo băng thông giữa hai node (cần cài iperf3)

```bash
iperf3 -s
iperf3 -c <peer-ip>
```

4. Đối chiếu OSD nào chậm

```bash
ceph osd perf
```

## Lưu ý

MTU phải đồng nhất trên toàn đường đi: NIC, bond, bridge, VLAN và switch. Nếu ping -M do báo "message too long" thì có điểm nào đó MTU nhỏ hơn.

<!-- từ khóa: ceph mạng network mtu jumbo rớt gói heartbeat slow ops osd flapping switch bond -->
