# PG down, peering kẹt hoặc unfound objects (mất nhiều OSD)

[← Mục lục](../../../README.md) · Case study Ceph

**Triệu chứng:** HEALTH_ERR, "N pgs down", pg ở trạng thái down+peering, IO vào một số object bị treo; hoặc "N unfound" (objects unfound).

**Nguyên nhân hay gặp:** Nhiều OSD cùng chứa bản sao của một PG bị mất lần lượt (OSD thứ nhất chết, chưa kịp chép dữ liệu mới thì OSD thứ hai chết), peering bị chặn vì chờ OSD đã down.

## Các bước xử lý

1. Xem PG nào down và có phải do peering không

```bash
ceph health detail
ceph pg dump_stuck inactive
```

2. Hỏi PG vì sao kẹt: phần recovery_state sẽ nói peering đang bị chặn bởi OSD nào

```bash
ceph pg <pgid> query
```

3. Cố gắng đưa OSD bị chặn sống lại trước (start service, sửa đĩa, đưa node về)

```bash
ceph osd tree down
systemctl start ceph-osd@<osd-id>
```

4. Với unfound: liệt kê object unfound và OSD có thể còn giữ bản sao

```bash
ceph pg <pgid> list_unfound
ceph pg <pgid> query
```

5. BIỆN PHÁP CUỐI, chỉ khi OSD chắc chắn không thể lấy lại: khai báo OSD mất rồi bỏ hoặc quay về bản cũ của object unfound (mất dữ liệu)

```bash
ceph osd lost <osd-id> --yes-i-really-mean-it
ceph pg <pgid> mark_unfound_lost revert
```

## Lưu ý

Hai lệnh ở bước cuối làm mất dữ liệu vĩnh viễn, tài liệu Ceph chỉ dùng khi đã hết cách lấy lại OSD. Chụp output của ceph pg query và ceph health detail trước khi chạy. Luôn ưu tiên đưa OSD cũ trở lại, kể cả đưa đĩa sang máy khác.

## Nguồn tham khảo

- [Ceph docs: Troubleshooting PGs](https://docs.ceph.com/en/reef/rados/troubleshooting/troubleshooting-pg/)

<!-- từ khóa: ceph pg down peering incomplete unfound objects mất dữ liệu osd lost mark_unfound_lost stuck inactive -->
