# OSD down hoặc up/down liên tục (flapping)

[← Mục lục](../../README.md)

**Triệu chứng:** ceph -s báo "N osds down", OSD lúc up lúc down, log có "wrongly marked me down" hoặc heartbeat_check no reply.

**Nguyên nhân hay gặp:** Tiến trình OSD crash, đĩa lỗi, host thiếu RAM (OOM killer), card mạng lỗi hoặc MTU không khớp làm mất heartbeat.

## Các bước xử lý

1. Xác định OSD nào đang down và ở host nào

```bash
ceph health detail
ceph osd tree down
```

2. Đọc log OSD quanh thời điểm rớt, tìm crash, I/O error, OOM

```bash
journalctl -u ceph-osd@<osd-id> --since "1 hour ago"
ceph crash ls
```

3. Trên host: kiểm tra OOM và lỗi đĩa

```bash
dmesg -T | grep -Ei 'oom|i/o error|blk_update'
smartctl -a /dev/<dev>
```

4. Nếu nghi mạng (nhiều OSD cùng host flap): xem lỗi NIC, MTU, heartbeat

```bash
ethtool -S <if>
ceph config get osd osd_heartbeat_grace
```

5. Nếu cần dừng OSD để xử lý: kiểm tra an toàn và đặt noout trước

```bash
ceph osd ok-to-stop <osd-id>
ceph osd set noout
```

6. Khởi động lại OSD, theo dõi nó vào lại, rồi gỡ noout

```bash
systemctl restart ceph-osd@<osd-id>
ceph osd stat
ceph osd unset noout
```

## Lưu ý

Đĩa lỗi thật (SMART xấu, I/O error lặp lại) thì thay đĩa, đừng restart mãi. Đừng out nhiều OSD cùng lúc khi cluster đang không khỏe.

<!-- từ khóa: ceph osd down flapping rớt osd heartbeat -->
