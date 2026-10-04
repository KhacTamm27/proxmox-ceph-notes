# Nâng cấp Ceph Quincy 17.2.8 → Reef 18.2.8 → Squid 19.2.4 trên PVE 8.4 (3 node, có CephFS)

[← Mục lục](../../README.md) · Runbook

**Mục tiêu:** Nâng Ceph hai bước liên tiếp (Quincy lên Reef, rồi Reef lên Squid) trên cluster 3 node hyper-converged (mỗi node có MON, MGR, OSD, MDS), PVE giữ nguyên 8.4. Ghi chú gốc dừng ở PVE 8.4 + Squid 19.2.4; bước tiếp theo là pve8to9.

**Điều kiện trước khi làm:** ceph -s = HEALTH_OK, toàn bộ OSD up/in, quorum MON đủ 3/3. Degraded phải về 0 mới nâng cấp; scrub, deep-scrub, backfilling chỉ cần theo dõi và ghi baseline (không bắt buộc dừng) miễn là không HEALTH_ERR và tốc độ ổn định. Ghi lại rank MDS nào đang active ở node nào để dự đoán failover. Làm tuần tự Node1 rồi Node2 rồi Node3, không nâng hai node cùng lúc.

## Các bước

1. Kiểm tra trạng thái trước khi bắt đầu (chạy một lần, từ node bất kỳ)

```bash
ceph -s
ceph health detail
ceph osd df tree
ceph mon stat
pvecm status
ceph fs status
ceph versions
```

2. Trên từng node: xác nhận repo hiện tại là quincy rồi đổi sang reef

```bash
cat /etc/apt/sources.list.d/ceph.list
sed -i 's/quincy/reef/' /etc/apt/sources.list.d/ceph.list
apt update
apt policy ceph-osd
```

3. Xác nhận Candidate là 18.2.8-pve1 từ đúng repo ceph-reef rồi mới cài thật, sau đó kiểm tra đã cài đúng bản

```bash
apt full-upgrade -y
apt policy ceph-osd
dpkg -l | grep ceph-osd
```

4. Maintain Ceph (chỉ một lần, áp dụng toàn cluster): đặt 6 cờ noout / nobackfill / norecover / norebalance / noscrub / nodeep-scrub (xem runbook bảo trì production)

```bash
ceph osd set noout
ceph osd set nobackfill
ceph osd set norecover
ceph osd set norebalance
ceph osd set noscrub
ceph osd set nodeep-scrub
```

5. Restart theo đúng thứ tự, từng lệnh kiểm tra ceph -s trước khi đi tiếp. MON trước, quorum phải còn đủ

```bash
systemctl restart ceph-mon.target
ceph -s
```

6. Tiếp theo MGR

```bash
systemctl restart ceph-mgr.target
ceph -s
```

7. Rồi OSD. Có thể tạm thấy peering hoặc X osds down, đợi 10 đến 15 giây rồi kiểm tra lại, không chạy thêm lệnh khác

```bash
systemctl restart ceph-osd.target
ceph -s
```

8. Cuối cùng MDS. Node giữ rank active của CephFS sẽ failover ngắn, đó là bình thường

```bash
systemctl restart ceph-mds.target
ceph -s
ceph fs status
```

9. Cách cẩn trọng hơn cho MDS khi max_mds lớn hơn 1 (ghi chú gốc): dừng hết MDS standby, đặt max_mds = 1, restart MDS active, rồi trả max_mds lại

```bash
ceph fs set <fsname> max_mds 1
systemctl stop ceph-mds@<standby-id>
systemctl restart ceph-mds@<active-id>
ceph fs set <fsname> max_mds 2
```

10. Khi cả 3 node xong: chốt phiên bản tối thiểu (bước này theo hướng dẫn Proxmox, ghi chú gốc chưa có), bỏ 6 cờ, theo dõi recovery

```bash
ceph osd require-osd-release reef
ceph osd unset noout
ceph osd unset nobackfill
ceph osd unset norecover
ceph osd unset norebalance
ceph osd unset noscrub
ceph osd unset nodeep-scrub
ceph versions
```

11. Bước 2, Reef lên Squid: lặp lại đúng quy trình trên, chỉ đổi repo. Candidate phải là 19.2.4-1~bpo12+1 từ ceph-squid

```bash
sed -i 's/reef/squid/' /etc/apt/sources.list.d/ceph.list
apt update
apt policy ceph-osd
apt full-upgrade -y
```

12. Sau Squid: restart MON, MGR, OSD, MDS như trên, rồi chốt phiên bản và bỏ cờ

```bash
ceph osd require-osd-release squid
ceph versions
```

## Lưu ý

Điều kiện đạt mỗi bước: HEALTH_OK và ceph versions cho mon/mgr/osd/mds đều đúng phiên bản mới. Trạng thái đạt được: PVE 8.4 + Ceph Squid 19.2.4. Bước kế tiếp là nâng PVE 8 lên 9 (pve8to9) khi Ceph đã ở Squid. Xem thêm case nâng cấp Ceph (có nguồn Proxmox wiki) và case MDS.

<!-- từ khóa: runbook nâng cấp upgrade ceph quincy reef squid pve 8.4 3 node hyper-converged cephfs mds mon mgr osd flags -->
