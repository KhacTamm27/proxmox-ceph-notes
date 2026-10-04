# Nâng cấp một node Proxmox VE từ 5.4 lên 8.x (qua 6, 7, 8) kèm ZFS

[← Mục lục](../../README.md) · Runbook

**Mục tiêu:** Nâng một node đơn Proxmox rất cũ (5.4, Debian stretch) lên 8.x theo chuỗi 5 lên 6 lên 7 lên 8, rồi import lại các zpool dữ liệu.

**Điều kiện trước khi làm:** Xác định chính xác đĩa boot (đơn hoặc ZFS RAID1), lưu WWN/SN để nếu hỏng có thể cài mới OS và import lại zpool. Backup /etc/network/interfaces, /etc/pve/, /etc/hosts. Ghi lại tên các zfs pool. Nên chạy bộ kiểm tra có sẵn của từng bản (pve5to6, pve6to7, pve7to8 --full) trước mỗi bước (gợi ý bổ sung, ghi chú gốc chưa có).

## Các bước

1. Chuẩn bị

```bash
zpool status rpool
lsblk -o NAME,SIZE,SERIAL,WWN
```

2. 5.x: thêm repo no-subscription (lưu ý đúng tên file sources.list và dùng dấu nháy thẳng)

```bash
echo "deb http://download.proxmox.com/debian/pve stretch pve-no-subscription" >> /etc/apt/sources.list
```

3. Debian stretch đã hết hỗ trợ nên repo cũ không dùng được. Comment các dòng ftp.debian.org / security.debian.org cũ và dùng archive.debian.org

```bash
deb http://archive.debian.org/debian stretch main contrib
deb http://archive.debian.org/debian stretch-updates main
deb http://archive.debian.org/debian-security stretch/updates main
```

4. Cập nhật lên bản mới nhất của 5.x rồi reboot

```bash
apt update
apt dist-upgrade
reboot
```

5. 5 lên 6: đổi suite, bỏ repo enterprise bằng cách thêm # vào /etc/apt/sources.list.d/pve-enterprise.list, nâng cấp. Các lựa chọn Y/N mặc định chọn N, rồi reboot để chạy kernel mới

```bash
sed -i 's/stretch/buster/g' /etc/apt/sources.list
apt update
apt dist-upgrade
reboot
```

6. 6 lên 7

```bash
sed -i 's/buster\/updates/bullseye-security/g;s/buster/bullseye/g' /etc/apt/sources.list
apt update
apt dist-upgrade
reboot
```

7. 7 lên 8

```bash
sed -i -e 's/bullseye/bookworm/g' /etc/apt/sources.list
apt update
apt dist-upgrade
reboot
```

8. Import lại các zpool DATA (theo tên, hoặc theo by-id), rồi nâng feature cho từng pool dữ liệu

```bash
zpool import
zpool import <pool-name> -f -d /dev/disk/by-id/
zpool upgrade <pool-name>
```

9. Kiểm tra toàn bộ dữ liệu của pool

```bash
zpool status <pool-name>
zfs list
```

## Lưu ý

Nếu apt báo không tìm thấy buster hoặc bullseye trên ftp.debian.org, các bản này cũng có thể đã chuyển sang archive.debian.org, đổi tương tự bước stretch. zpool upgrade không hoàn tác được và chỉ nên chạy cho pool dữ liệu, không chạy cho rpool nếu chưa chắc bootloader hỗ trợ các feature mới (có thể làm node không boot). Cluster nhiều node thì phải theo hướng dẫn chính thức của Proxmox vì còn bước nâng corosync, bài này chỉ cho node đơn.

<!-- từ khóa: runbook nâng cấp upgrade proxmox 5.4 6 7 8 stretch buster bullseye bookworm single node zfs rpool zpool import upgrade apt dist-upgrade -->
