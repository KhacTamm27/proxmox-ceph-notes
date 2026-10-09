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

## Lưu ý

Linux bonding mode: balance-rr (0) chia vòng các gói, thường cần switch hỗ trợ cấu hình tương ứng; active-backup (1) chỉ một NIC active, không cần LACP trên switch; balance-xor (2) hash luồng, cấu hình switch phải phù hợp; broadcast (3) gửi trên mọi slave, hiếm dùng; 802.3ad (4) là LACP, hai phía phải cùng LAG và switch cho phép VLAN cần dùng; balance-tlb (5) cân bằng tải gửi, không cần cấu hình switch đặc biệt; balance-alb (6) cân bằng gửi/nhận, cần kiểm tra tương thích mạng. bond-primary chỉ có ý nghĩa với active-backup, không đặt cùng 802.3ad. `bond-miimon 100` theo dõi link mỗi 100 ms; `bond-xmit-hash-policy layer2+3` chọn luồng theo MAC/IP để phân tải, không làm một luồng đơn lẻ vượt băng thông một NIC. OVS có cú pháp mode riêng: active-backup, balance-slb hoặc balance-tcp; balance-tcp cần cấu hình LACP tương ứng ở cả OVS và switch, không đồng nghĩa tự bật LACP chỉ vì đặt bond_mode. Trunk là danh sách VLAN được phép đi qua: trên Linux bridge dùng `bridge-vlan-aware yes` và `bridge-vids`; trên switch cũng phải allow đúng VLAN. `tag=70` của VM/CT hoặc OVSIntPort là VLAN access/tagged cho một VLAN, không phải danh sách trunk; cấu hình trunk của NIC VM/CT dùng trường VLAN trunks trong Proxmox và phải giới hạn cùng danh sách allowed VLAN ở bridge/switch. Cấu hình mẫu Linux dùng `bond0` làm port của VLAN-aware bridge; `vmbr0.70` đặt IP host trên VLAN 70. Không trộn `bond0.<VID>` làm bridge port với mô hình VLAN-aware nếu chưa chủ ý thiết kế single-VLAN bridge. Luôn kiểm tra MTU xuyên suốt NIC/bond/bridge/VLAN/switch. Thay đổi mạng có thể làm mất phiên SSH/GUI; giữ console/IPMI và không reload từ xa nếu không có đường khôi phục.

## Nguồn tham khảo

- [Proxmox VE Administration Guide: Network Configuration](https://pve.proxmox.com/pve-docs/pve-admin-guide.html#sysadmin_network_configuration)
- [Linux kernel: Bonding driver](https://www.kernel.org/doc/Documentation/networking/bonding.txt)

<!-- từ khóa: proxmox pve network networking mạng bridge linux bridge ovs openvswitch bond bond-mode bond_mode active-backup balance-rr balance-xor broadcast 802.3ad lacp trunk vlan allow vlan-aware bridge-vids switch port-channel nic teaming cấu hình mạng -->
