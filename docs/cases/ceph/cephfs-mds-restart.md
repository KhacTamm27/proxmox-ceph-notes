# CephFS: MDS failover khi restart hoặc nâng cấp (max_mds lớn hơn 1)

[← Mục lục](../../../README.md) · Case study Ceph

**Triệu chứng:** Restart ceph-mds.target hoặc nâng cấp làm CephFS gián đoạn ngắn, trạng thái MDS tạm là replay, reconnect hoặc rejoin.

**Nguyên nhân hay gặp:** Node đang giữ rank active của CephFS sẽ failover sang standby khi MDS restart. Gián đoạn ngắn là bình thường. Với max_mds lớn hơn 1 (nhiều rank active) cần cẩn thận hơn.

## Các bước xử lý

1. Trước khi làm: ghi lại rank nào active ở node nào để dự đoán failover

```bash
ceph fs status
```

2. Quy trình cẩn trọng cho MDS (theo ghi chú nâng cấp): đặt max_mds = 1, dừng hết MDS standby

```bash
ceph fs set <fsname> max_mds 1
systemctl stop ceph-mds@<standby-id>
```

3. Nâng cấp hoặc restart MDS active, kiểm tra CephFS truy cập bình thường

```bash
systemctl restart ceph-mds@<active-id>
ceph fs status
```

4. Bật lại các standby và trả max_mds về giá trị cũ

```bash
systemctl start ceph-mds@<standby-id>
ceph fs set <fsname> max_mds 2
```

## Lưu ý

Nếu vận hành giữ nguyên max_mds = 2 trong nâng cấp (như ghi chú gốc), vẫn chấp nhận failover ngắn khi restart từng node nhưng phải kiểm tra ceph -s và ceph fs status sau mỗi lần restart. Làm từng node một.

<!-- từ khóa: ceph cephfs mds failover restart nâng cấp max_mds standby active rank ceph fs status -->
