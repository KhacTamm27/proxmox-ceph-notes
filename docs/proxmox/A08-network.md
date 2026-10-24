# A8 · Mạng

[← Mục lục](../../README.md) · Proxmox host · 23 lệnh · tên gốc: Network

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← A7 HA và replication](../proxmox/A07-high-availability-and-replication.md) · [A9 Tường lửa →](../proxmox/A09-firewall.md)

## Interface (Interfaces)

```bash
# [chỉ đọc] Xem địa chỉ IP ngắn gọn | Addresses, brief
# từ khóa: ip địa chỉ interface xem node quản trị mac
ip -br a

# [chỉ đọc] Chi tiết interface, VLAN, bond | Link details, VLAN, bond
# từ khóa: interface vlan bond chi tiết
ip -d link show <if>

# [chỉ đọc] Bộ đếm lỗi và gói của interface | Interface counters
# từ khóa: lỗi mạng drop rớt gói error counter
ip -s link show <if>

# [chỉ đọc] Bảng định tuyến | Routing table
# từ khóa: route định tuyến gateway
ip r
```

## Bridge

```bash
# [chỉ đọc] Các cổng của bridge | Bridge ports
# từ khóa: bridge cổng
bridge link

# [chỉ đọc] Bảng VLAN trên bridge | VLAN table
# từ khóa: vlan bridge
bridge vlan show
```

## Bond

```bash
# [chỉ đọc] Trạng thái bond và LACP | Bond and LACP state
# từ khóa: bond lacp active-backup lỗi bond link down
cat /proc/net/bonding/bond0
```

## Cấu hình (Config)

```bash
# [chỉ đọc] Xem cấu hình mạng | Network config
# từ khóa: cấu hình mạng interfaces đổi ip node ip quản trị gateway sửa ip vmbr0 bond vlan
cat /etc/network/interfaces

# Áp dụng cấu hình mạng không cần reboot | Apply network config
# từ khóa: áp dụng mạng reload ifupdown2
ifreload -a
```

## NIC

```bash
# [chỉ đọc] Tốc độ, duplex, trạng thái link | Speed, duplex, link
# từ khóa: tốc độ link duplex nic cổng 1g 10g up down
ethtool <if>

# [chỉ đọc] Thống kê lỗi card mạng trên host OSD | NIC statistics, errors, drops
# từ khóa: nic lỗi mạng drop crc flapping
ethtool -S <if>

# [chỉ đọc] Driver và firmware của card mạng | Driver and firmware
# từ khóa: driver firmware nic
ethtool -i <if>

# [chỉ đọc] Các tính năng offload của card mạng | Offload features
# từ khóa: offload tso gso
ethtool -k <if>
```

## Kiểm tra MTU (MTU test)

```bash
# [chỉ đọc] Kiểm tra MTU 9000 thông suốt đầu cuối | Verify MTU 9000 end to end
# từ khóa: mtu jumbo ping lệch mtu mạng ceph
ping -M do -s 8972 <ip>
```

## Băng thông (Throughput)

```bash
# Đo băng thông giữa hai máy | Bandwidth test
# từ khóa: băng thông bandwidth iperf mạng chậm
iperf3 -s / iperf3 -c <ip> -P 4
```

## Cổng đang mở (Sockets)

```bash
# [chỉ đọc] Các cổng đang lắng nghe | Listening ports
# từ khóa: cổng port listen dịch vụ
ss -tulpn
```

## Bắt gói (Capture)

```bash
# [chỉ đọc] Bắt gói tin theo host | Packet capture
# từ khóa: bắt gói tcpdump capture
tcpdump -i <if> -nn host <ip>
```

## Đường đi mạng (Path)

```bash
# [chỉ đọc] Đường đi và tỉ lệ mất gói | Path and loss
# từ khóa: đường đi mất gói traceroute
mtr <ip>
```

## Thiết bị lân cận (Neighbors)

```bash
# [chỉ đọc] Xem switch hàng xóm qua LLDP (nếu có lldpd) | LLDP switch neighbors (if lldpd)
# từ khóa: lldp switch cổng
lldpcli show neighbors
```

## OVS

```bash
# [chỉ đọc] Cấu trúc Open vSwitch (nếu dùng) | Open vSwitch layout (if used)
# từ khóa: ovs openvswitch
ovs-vsctl show
```

## QoS

```bash
# [chỉ đọc] Thống kê hàng đợi gói của interface | Queue discipline stats
# từ khóa: qdisc queue drop
tc -s qdisc show dev <if>

# [chỉ đọc] Quy tắc đánh dấu DSCP | DSCP marking rules
# từ khóa: dscp qos mangle
iptables -t mangle -S

# [chỉ đọc] Xem toàn bộ quy tắc nftables | nftables rules
# từ khóa: nftables firewall rule
nft list ruleset
```

## Case và runbook dùng lệnh trong nhóm này

- [Cấu hình mạng Proxmox: OVS/Linux bridge, bond, LACP và VLAN trunk](../cases/pve/pve-network-bridge-bond-vlan.md)
- [Mạng Ceph: MTU không khớp, nghẽn hoặc rớt gói](../cases/ceph/network-mtu.md)
- [Corosync link chập chờn, retransmit, node tự reboot (HA watchdog)](../cases/pve/corosync-flapping.md)
- [OSD down hoặc up/down liên tục (flapping)](../cases/ceph/osd-down-flapping.md)
- [Slow ops / blocked requests (Ceph chậm, IO bị chặn)](../cases/ceph/slow-ops.md)
- [Latency OSD cao, IOPS thấp do SSD consumer (không có PLP)](../cases/ceph/osd-latency-consumer-ssd.md)
- [Cấu hình Nginx proxy console cho VM Proxmox (noVNC qua portal)](../runbooks/rb-console-proxy-nginx.md)
