# Cluster đầy khẩn cấp: ghi bị chặn (OSD_FULL), backfill_toofull

[← Mục lục](../../../README.md) · Case study Ceph

**Triệu chứng:** HEALTH_ERR "full osd(s)", VM không ghi được, PG có backfill_toofull hoặc recovery_toofull nên recovery không chạy.

**Nguyên nhân hay gặp:** Một hoặc vài OSD vượt ngưỡng full (mặc định 95%) do dữ liệu tăng nhanh hoặc phân bố lệch; Ceph chặn ghi để tránh hỏng dữ liệu. Snapshot và rác RGW chưa gc cũng giữ dung lượng.

## Các bước xử lý

1. Xác định OSD nào full và mức chung của cluster

```bash
ceph health detail
ceph df
ceph osd df tree
```

2. Giải phóng chỗ trước: xóa snapshot, image RBD cũ, dữ liệu không quan trọng; nếu có RGW thì chạy gc

```bash
radosgw-admin gc process
```

3. Chỉ khi không còn cách nào: tăng nhẹ ngưỡng full để mở lại ghi, đủ để xóa dữ liệu (nguy hiểm)

```bash
ceph osd set-full-ratio 0.96
```

4. Khi đã thoát khỏi tình trạng đầy, trả về mặc định và rebalance

```bash
ceph osd set-full-ratio 0.95
ceph osd reweight-by-utilization
```

5. Dài hạn: thêm OSD hoặc node, theo dõi PG backfill

```bash
ceph -s
```

## Lưu ý

Nâng ngưỡng full chỉ là mượn thêm vài phần trăm, OSD chạm 100% có thể không khởi động lại được. Cảnh báo theo OSD đầy nhất chứ không theo mức trung bình của cluster. Cluster nên giữ dưới khoảng 80% để còn chỗ cho recovery.

## Nguồn tham khảo

- [Ceph docs: Health checks](https://docs.ceph.com/en/mimic/rados/operations/health-checks)
- [Netdata: Ceph OSD_FULL](https://www.netdata.cloud/guides/ceph/ceph-osd-full/)
- [Netdata: backfill_toofull](https://www.netdata.cloud/guides/ceph/ceph-backfill-toofull/)

<!-- từ khóa: ceph full osd_full cluster đầy không ghi được backfill_toofull recovery toofull đầy khẩn cấp gc snapshot -->
