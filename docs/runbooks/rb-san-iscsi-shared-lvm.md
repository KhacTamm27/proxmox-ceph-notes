# SAN iSCSI + Shared LVM cho cluster Proxmox, và mở rộng dung lượng online (pvmove)

[← Mục lục](../../README.md) · Runbook

**Mục tiêu:** Cho 3 node Proxmox cùng đăng nhập một LUN iSCSI và dùng chung một Volume Group (Shared LVM) để chia volume cho VM; sau đó mở rộng dung lượng không mất dữ liệu, không downtime.

**Điều kiện trước khi làm:** Một máy storage làm iSCSI target, 3 node Proxmox truy cập được tới nó. Mô hình: các node, iSCSI initiator, iSCSI target, LUN, Shared LVM, mỗi LV là một đĩa VM.

## Các bước

1. Trên máy storage: cài và cấu hình iSCSI target (block backstore). Các lệnh trong targetcli shell

```bash
apt install targetcli-fb -y
targetcli
cd /backstores/block
create pve-lun1 /dev/<dev>
cd /iscsi
create <iqn>
cd /iscsi/<iqn>/tpg1/luns
create /backstores/block/pve-lun1
cd /
saveconfig
exit
```

2. Trên MỖI node Proxmox: cài initiator, discovery, login

```bash
apt install open-iscsi -y
systemctl enable --now iscsid
iscsiadm -m discovery -t sendtargets -p <IP_TARGET>:3260
iscsiadm -m node --targetname <iqn> --portal <IP_TARGET>:3260 --login
iscsiadm -m session
lsblk
```

3. Trên GUI: Datacenter, Storage, Add, iSCSI (Portal, Target, bỏ tick Use LUNs directly, Nodes = All). Rồi Add, LVM: Base storage = iSCSI vừa tạo, Volume group đặt tên không khoảng trắng hay ký tự lạ, tick Shared, Nodes = All

4. Kiểm tra trên từng node

```bash
pvesm status
vgs
```

5. Mở rộng, bước 1: tạo LUN mới trên iSCSI target

```bash
targetcli
cd /backstores/block
create pve-lun2 /dev/<new-dev>
cd /iscsi/<iqn>/tpg1/luns
create /backstores/block/pve-lun2
cd /
saveconfig
exit
```

6. Bước 2: rescan trên cả 3 node để nhận LUN mới

```bash
iscsiadm -m session --rescan
lsblk
```

7. Bước 3: trên MỘT node, thêm PV mới vào VG. Trước đó kiểm tra VG còn đủ free extent trên PV đích để chứa dữ liệu từ PV nguồn

```bash
vgs
pvcreate /dev/<new-dev>
vgextend <vg-name> /dev/<new-dev>
```

8. Bước 4: chuyển dữ liệu từ PV cũ sang PV mới (online, VM vẫn chạy). Nên làm ngoài giờ cao điểm

```bash
pvmove /dev/<old-dev> /dev/<new-dev>
```

9. Bước 5: gỡ PV cũ khỏi VG

```bash
vgreduce <vg-name> /dev/<old-dev>
pvremove /dev/<old-dev>
```

10. Bước 6: trên 2 node còn lại chỉ cần làm mới cache, không cần pvcreate hay vgextend lại

```bash
pvscan --cache
vgscan
```

11. Bước 7: xác nhận dung lượng mới trên cả 3 node

```bash
pvesm status
vgs
```

## Lưu ý

Cấu hình target trong ghi chú gốc (authentication=0, generate_node_acls=1, demo_mode_write_protect=0) cho phép truy cập không xác thực, chỉ phù hợp lab. Production nên giới hạn ACL theo IQN của từng node và bật CHAP. Dù về lý thuyết pvmove không gây downtime, nó tạo tải I/O khi copy dữ liệu.

<!-- từ khóa: runbook san iscsi lvm shared targetcli open-iscsi lun volume group pvmove vgextend mở rộng dung lượng block storage -->
