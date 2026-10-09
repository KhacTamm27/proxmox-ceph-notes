# Cấu hình mạng Proxmox: OVS/Linux bridge, bond, LACP và VLAN trunk

[← Mục lục](../../../README.md) · Case study Proxmox cluster

**Triệu chứng:** VM/CT mất mạng hoặc không nhận VLAN; host mất IP quản trị sau khi sửa /etc/network/interfaces; bond chỉ chạy một link hoặc LACP không lên; VLAN tag/trunk không thông suốt.

**Nguyên nhân hay gặp:** Nhầm OVS với Linux bridge; cấu hình bond không khớp mode ở switch; thiếu VLAN allowed trên switch/bridge; nhầm VLAN tag của host interface với VLAN trunk cho VM; MTU không đồng nhất; dùng bond-primary cùng mode 802.3ad.

## Các bước xử lý

1. Chọn một mô hình bridge cho mỗi đường đi mạng và lưu bản backup trước khi thay đổi cấu hình

```bash
cp /etc/network/interfaces /etc/network/interfaces.bak
cat /etc/network/interfaces
```

2. Tham khảo ví dụ OVS: bond active-backup, OVS bridge và host VLAN 70 qua OVSIntPort

**`/etc/network/interfaces`**

```ini
auto lo
iface lo inet loopback

auto enp24s0f0np0
iface enp24s0f0np0 inet manual

auto enp24s0f1np1
iface enp24s0f1np1 inet manual

auto bond0
iface bond0 inet manual
        ovs_bonds enp24s0f0np0 enp24s0f1np1
        ovs_type OVSBond
        ovs_bridge vmbr0
        ovs_options bond_mode=active-backup

auto vlan70
iface vlan70 inet static
        address 192.168.70.147/24
        gateway 192.168.70.1
        ovs_type OVSIntPort
        ovs_bridge vmbr0
        ovs_options tag=70

auto vmbr0
iface vmbr0 inet manual
        ovs_type OVSBridge
        ovs_ports bond0 vlan70

source /etc/network/interfaces.d/*
```

3. Tham khảo ví dụ Linux bridge VLAN-aware: bond LACP, allow-list VLAN 10/20/70 và IP quản trị trên VLAN 70

**`/etc/network/interfaces`**

```ini
auto lo
iface lo inet loopback

auto enp24s0f0np0
iface enp24s0f0np0 inet manual

auto enp24s0f1np1
iface enp24s0f1np1 inet manual

auto bond0
iface bond0 inet manual
        bond-slaves enp24s0f0np0 enp24s0f1np1
        bond-miimon 100
        bond-mode 802.3ad
        bond-xmit-hash-policy layer2+3
        mtu 9000

auto vmbr0
iface vmbr0 inet manual
        bridge-ports bond0
        bridge-stp off
        bridge-fd 0
        bridge-vlan-aware yes
        bridge-vids 10 20 70
        mtu 9000

auto vmbr0.70
iface vmbr0.70 inet static
        address 10.2.70.147/24
        gateway 10.2.70.1
        mtu 9000

source /etc/network/interfaces.d/*
```

4. Đối chiếu trạng thái bond, bridge, VLAN và link vật lý trên node

```bash
cat /proc/net/bonding/bond0
bridge link
bridge vlan show
ip -s link show <if>
ovs-vsctl show
```

5. Kiểm tra cấu hình NIC của VM/CT và VLAN ID được phép trên switch

```bash
qm config <vmid>
pct config <ctid>
```

6. Chỉ áp dụng sau khi xác nhận đường quản trị dự phòng hoặc có console out-of-band; theo dõi lại IP và kết nối sau reload

```bash
ifreload -a
ip -br a
ip r
```

## Tham khảo nhanh

- **Linux bond · balance-rr (mode 0):** Gửi luân phiên qua các NIC; switch cần static port-channel/EtherChannel, không bật LACP cho nhóm này. Thường không khuyến nghị cho môi trường phổ thông.
- **Linux bond · active-backup (mode 1):** Một NIC active, NIC còn lại dự phòng; switch không cần LACP/port-channel. `bond-primary` chỉ dùng với mode này.
- **Linux bond · balance-xor (mode 2):** Hash luồng để chọn NIC; cấu hình switch thành static port-channel/EtherChannel, không dùng LACP.
- **Linux bond · broadcast (mode 3):** Gửi bản sao qua mọi NIC; không bật LACP. Có thể gây MAC flapping/duplicate traffic, chỉ dùng khi thiết kế mạng yêu cầu.
- **Linux bond · 802.3ad (mode 4, LACP):** Hai đầu phải nằm trong cùng LAG; đặt LACP active trên switch (active/passive cũng được nếu đầu còn lại active). Ví dụ `bond-mode 802.3ad`; không dùng `bond-primary`.
- **Linux bond · balance-tlb (mode 5):** Cân bằng tải gửi, không cần LACP hay cấu hình port-channel trên switch.
- **Linux bond · balance-alb (mode 6):** Cân bằng tải gửi/nhận, không cần LACP/port-channel; kiểm tra tương thích switch, ARP và các thiết bị trong cùng mạng.
- **OVS bond · active-backup:** Failover, chỉ một link chuyển traffic tại một thời điểm; switch không cần LACP/port-channel.
- **OVS bond · balance-slb:** Phân tải theo source MAC; không cần LACP hay cấu hình port-channel trên switch.
- **OVS bond · balance-tcp:** Phân tải theo luồng TCP; bật LACP cả hai đầu. Trên OVS dùng `bond_mode=balance-tcp lacp=active`; switch cấu hình LAG với LACP active (hoặc passive nếu OVS active). Chỉ đặt `bond_mode=balance-tcp` là chưa đủ để bật LACP.
- **VLAN trunk · Linux bridge / OVS / switch:** LACP và VLAN trunk là hai cấu hình riêng. Linux bridge dùng `bridge-vlan-aware yes` + `bridge-vids 10 20 70`; NIC VM/CT dùng `tag=70` cho một VLAN hoặc `trunks=10;20;70` cho trunk. OVS và switch phải allow đúng VLAN trên port/LAG; không nhầm tag đơn với trunk.

## Lưu ý

`bond-miimon 100` kiểm tra link mỗi 100 ms; `bond-xmit-hash-policy layer2+3` chọn luồng theo MAC/IP, không làm một luồng đơn vượt băng thông của một NIC. Luôn kiểm tra MTU xuyên suốt NIC/bond/bridge/VLAN/switch. Thay đổi mạng có thể làm mất SSH/GUI; giữ console/IPMI và không reload từ xa nếu chưa có đường khôi phục.

## Nguồn tham khảo

- [Proxmox VE Administration Guide: Network Configuration](https://pve.proxmox.com/pve-docs/pve-admin-guide.html#sysadmin_network_configuration)
- [Linux kernel: Bonding driver](https://www.kernel.org/doc/Documentation/networking/bonding.txt)
- [Open vSwitch: Bonding FAQ](https://docs.openvswitch.org/en/latest/faq/bonding/)

<!-- từ khóa: proxmox pve network networking mạng bridge linux bridge ovs openvswitch bond bond-mode bond_mode active-backup balance-rr balance-xor broadcast 802.3ad lacp trunk vlan allow vlan-aware bridge-vids switch port-channel nic teaming cấu hình mạng -->
