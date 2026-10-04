# BLUEFS_SPILLOVER: metadata RocksDB tràn sang đĩa chậm

[← Mục lục](../../../README.md) · Case study Ceph

**Triệu chứng:** HEALTH_WARN "BlueFS spillover detected on N OSD(s)", latency của các OSD HDD tăng.

**Nguyên nhân hay gặp:** Phân vùng DB/WAL trên SSD/NVMe quá nhỏ so với dung lượng OSD (hoặc omap tăng nhiều, ví dụ bucket index RGW) nên metadata phải ghi xuống đĩa dữ liệu chậm.

## Các bước xử lý

1. Xem OSD nào bị và mức tràn

```bash
ceph health detail
```

2. Đo lượng dữ liệu đang nằm trên đĩa chậm (slow_used_bytes lớn hơn 0 là đang tràn)

```bash
ceph daemon osd.<osd-id> perf dump bluefs
```

3. Giảm tạm thời bằng compact (cảnh báo có thể quay lại)

```bash
ceph tell osd.<osd-id> compact
```

4. Xử lý gốc: mở rộng thiết bị DB, hoặc dừng OSD rồi chuyển dữ liệu tràn về lại DB bằng công cụ bluestore

```bash
systemctl stop ceph-osd@<osd-id>
ceph-bluestore-tool bluefs-bdev-migrate --path /var/lib/ceph/osd/ceph-<osd-id> --devs-source /var/lib/ceph/osd/ceph-<osd-id>/block --dev-target /var/lib/ceph/osd/ceph-<osd-id>/block.db
systemctl start ceph-osd@<osd-id>
```

## Lưu ý

Mức khuyến nghị tham khảo là DB khoảng 4% dung lượng OSD. Có thể tắt cảnh báo bằng ceph config set osd bluestore_warn_on_bluefs_spillover false nhưng đó chỉ là che cảnh báo, không giải quyết nguyên nhân. Làm lần lượt từng OSD, kiểm tra noout/ok-to-stop trước khi dừng.

## Nguồn tham khảo

- [Netdata: Ceph BlueStore DB spillover](https://www.netdata.cloud/guides/ceph/ceph-bluestore-db-spillover/)
- [Red Hat: BlueFS spillover warning](https://access.redhat.com/node/4820151)

<!-- từ khóa: ceph bluefs spillover db wal ssd nvme hdd metadata tràn rocksdb chậm cảnh báo bluestore -->
