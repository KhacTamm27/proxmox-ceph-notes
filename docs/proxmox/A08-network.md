# A8 · Network

[← Mục lục](../../README.md) · Proxmox host · 23 lệnh

[← A7 High availability and replication](../proxmox/A07-high-availability-and-replication.md) · [A9 Firewall →](../proxmox/A09-firewall.md)

## Interfaces

```bash
# Xem địa chỉ IP ngắn gọn | Addresses, brief
# từ khóa: ip địa chỉ interface
ip -br a

# Chi tiết interface, VLAN, bond | Link details, VLAN, bond
# từ khóa: interface vlan bond chi tiết
ip -d link show <if>

# Bộ đếm lỗi và gói của interface | Interface counters
# từ khóa: lỗi mạng drop rớt gói error counter
ip -s link show <if>

# Bảng định tuyến | Routing table
# từ khóa: route định tuyến gateway
ip r
```

## Bridge

```bash
# Các cổng của bridge | Bridge ports
# từ khóa: bridge cổng
bridge link

# Bảng VLAN trên bridge | VLAN table
# từ khóa: vlan bridge
bridge vlan show
```

## Bond

```bash
# Trạng thái bond và LACP | Bond and LACP state
# từ khóa: bond lacp active-backup lỗi bond link down
cat /proc/net/bonding/bond0
```

## Config

```bash
# Xem cấu hình mạng | Network config
# từ khóa: cấu hình mạng interfaces
cat /etc/network/interfaces

# Áp dụng cấu hình mạng không cần reboot | Apply network config
# từ khóa: áp dụng mạng reload ifupdown2
ifreload -a
```

## NIC

```bash
# Tốc độ, duplex, trạng thái link | Speed, duplex, link
# từ khóa: tốc độ link duplex nic
ethtool <if>

# Thống kê lỗi card mạng trên host OSD | NIC statistics, errors, drops
# từ khóa: nic lỗi mạng drop crc flapping
ethtool -S <if>

# Driver và firmware của card mạng | Driver and firmware
# từ khóa: driver firmware nic
ethtool -i <if>

# Các tính năng offload của card mạng | Offload features
# từ khóa: offload tso gso
ethtool -k <if>
```

## MTU test

```bash
# Kiểm tra MTU 9000 thông suốt đầu cuối | Verify MTU 9000 end to end
# từ khóa: mtu jumbo ping lệch mtu mạng ceph
ping -M do -s 8972 <ip>
```

## Throughput

```bash
# Đo băng thông giữa hai máy | Bandwidth test
# từ khóa: băng thông bandwidth iperf mạng chậm
iperf3 -s / iperf3 -c <ip> -P 4
```

## Sockets

```bash
# Các cổng đang lắng nghe | Listening ports
# từ khóa: cổng port listen dịch vụ
ss -tulpn
```

## Capture

```bash
# Bắt gói tin theo host | Packet capture
# từ khóa: bắt gói tcpdump capture
tcpdump -i <if> -nn host <ip>
```

## Path

```bash
# Đường đi và tỉ lệ mất gói | Path and loss
# từ khóa: đường đi mất gói traceroute
mtr <ip>
```

## Neighbors

```bash
# Xem switch hàng xóm qua LLDP (nếu có lldpd) | LLDP switch neighbors (if lldpd)
# từ khóa: lldp switch cổng
lldpcli show neighbors
```

## OVS

```bash
# Cấu trúc Open vSwitch (nếu dùng) | Open vSwitch layout (if used)
# từ khóa: ovs openvswitch
ovs-vsctl show
```

## QoS

```bash
# Thống kê hàng đợi gói của interface | Queue discipline stats
# từ khóa: qdisc queue drop
tc -s qdisc show dev <if>

# Quy tắc đánh dấu DSCP | DSCP marking rules
# từ khóa: dscp qos mangle
iptables -t mangle -S

# Xem toàn bộ quy tắc nftables | nftables rules
# từ khóa: nftables firewall rule
nft list ruleset
```
