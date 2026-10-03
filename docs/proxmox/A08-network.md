# A8 · Network

[← Mục lục](../../README.md) · Proxmox host · 23 lệnh

[← A7 High availability and replication](../proxmox/A07-high-availability-and-replication.md) · [A9 Firewall →](../proxmox/A09-firewall.md)

## Interfaces

```bash
# Addresses, brief
ip -br a

# Link details, VLAN, bond
ip -d link show <if>

# Interface counters
ip -s link show <if>

# Routing table
ip r
```

## Bridge

```bash
# Bridge ports
bridge link

# VLAN table
bridge vlan show
```

## Bond

```bash
# Bond and LACP state
cat /proc/net/bonding/bond0
```

## Config

```bash
# Network config
cat /etc/network/interfaces

# Apply network config
ifreload -a
```

## NIC

```bash
# Speed, duplex, link
ethtool <if>

# Thống kê lỗi card mạng trên host OSD | NIC statistics, errors, drops
# từ khóa: nic lỗi mạng drop crc flapping
ethtool -S <if>

# Driver and firmware
ethtool -i <if>

# Offload features
ethtool -k <if>
```

## MTU test

```bash
# Verify MTU 9000 end to end
ping -M do -s 8972 <ip>
```

## Throughput

```bash
# Bandwidth test
iperf3 -s / iperf3 -c <ip> -P 4
```

## Sockets

```bash
# Listening ports
ss -tulpn
```

## Capture

```bash
# Packet capture
tcpdump -i <if> -nn host <ip>
```

## Path

```bash
# Path and loss
mtr <ip>
```

## Neighbors

```bash
# LLDP switch neighbors (if lldpd)
lldpcli show neighbors
```

## OVS

```bash
# Open vSwitch layout (if used)
ovs-vsctl show
```

## QoS

```bash
# Queue discipline stats
tc -s qdisc show dev <if>

# DSCP marking rules
iptables -t mangle -S

# nftables rules
nft list ruleset
```
