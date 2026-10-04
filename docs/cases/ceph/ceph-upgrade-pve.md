# Nâng cấp Ceph trên Proxmox (ví dụ Reef lên Squid)

[← Mục lục](../../../README.md) · Case study Ceph

**Triệu chứng:** Cần nâng cấp phiên bản Ceph mà không làm gián đoạn VM; sau nâng cấp có cảnh báo require-osd-release.

**Nguyên nhân hay gặp:** Nâng cấp Ceph phải đi đúng thứ tự: MON rồi MGR rồi OSD, và phải chốt require-osd-release sau cùng.

## Các bước xử lý

1. Trước khi bắt đầu: cluster phải HEALTH_OK, biết phiên bản hiện tại

```bash
ceph -s
ceph versions
```

2. Đặt noout cho cả quá trình

```bash
ceph osd set noout
```

3. Đổi repository Ceph sang bản mới (theo hướng dẫn chính thức) rồi nâng cấp gói trên từng node

```bash
sed -i "s/reef/squid/" /etc/apt/sources.list.d/ceph.list
apt update
apt full-upgrade
```

4. Restart theo thứ tự, từng node một: MON trước, kiểm tra min_mon_release

```bash
systemctl restart ceph-mon.target
ceph mon dump | grep min_mon_release
```

5. Tiếp theo MGR, kiểm tra các mgr chạy

```bash
systemctl restart ceph-mgr.target
ceph -s
```

6. Cuối cùng OSD, từng node một, chờ PG active+clean giữa các node

```bash
systemctl restart ceph-osd.target
ceph osd stat
```

7. Chốt phiên bản và gỡ noout

```bash
ceph osd require-osd-release squid
ceph osd unset noout
```

## Lưu ý

Không bỏ qua phiên bản trung gian (Proxmox khuyến nghị lên Reef trước khi lên Squid). Đảm bảo không còn OSD kiểu FileStore. Quên ceph osd unset noout là lỗi hay gặp. Luôn đọc trang hướng dẫn nâng cấp tương ứng trên pve.proxmox.com vì từng phiên bản có lưu ý riêng.

## Nguồn tham khảo

- [Proxmox wiki: Ceph Reef to Squid](https://pve.proxmox.com/wiki/Ceph_Reef_to_Squid)
- [Proxmox wiki: Ceph Quincy to Reef](https://pve.proxmox.com/wiki/Ceph_Quincy_to_Reef)

<!-- từ khóa: ceph upgrade nâng cấp reef squid quincy mon mgr osd require-osd-release noout proxmox ceph.list repository -->
