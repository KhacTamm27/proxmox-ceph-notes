# Ceph cảnh báo OSD device có nguy cơ hỏng

[← Mục lục](../../../README.md) · Case study Ceph

**Triệu chứng:** Ceph báo device health hoặc thiết bị có dự đoán tuổi thọ thấp; một OSD vẫn up nhưng SMART/NVMe metrics xấu hoặc thiết bị bị đánh dấu out do dự đoán lỗi.

**Nguyên nhân hay gặp:** Chỉ số SMART/NVMe cho thấy lỗi media, độ mòn cao hoặc Ceph devicehealth dự đoán thiết bị có thể hỏng. Cơ chế self-heal có thể tự đánh dấu OSD out nếu được bật và vượt ngưỡng.

## Các bước xử lý

1. Xem health detail và danh sách thiết bị, dự đoán tuổi thọ

```bash
ceph health detail
ceph device ls
```

2. Ánh xạ thiết bị nghi vấn về đúng OSD và node

```bash
ceph device ls-by-daemon osd.<id>
ceph device info <devid>
ceph osd metadata <osd-id>
```

3. Đọc metrics Ceph và xác minh trực tiếp SMART/NVMe trên node chứa OSD

```bash
ceph device get-health-metrics <devid>
smartctl -a /dev/<dev>
```

4. Nếu cần dữ liệu mới, scrape metrics của thiết bị rồi yêu cầu Ceph đánh giá lại health

```bash
ceph device scrape-health-metrics <devid>
ceph device check-health
```

5. Nếu SMART xác nhận đĩa suy giảm: thay theo case Thay đĩa OSD hỏng; chỉ destroy khi safe-to-destroy cho phép

```bash
ceph osd safe-to-destroy <osd-id>
ceph -s
```

## Lưu ý

Dự đoán sức khỏe là tín hiệu để điều tra, không phải bằng chứng chắc chắn đĩa sẽ hỏng; đối chiếu SMART/NVMe, log kernel và tải thực tế. Kiểm tra cấu hình devicehealth self-heal trước khi thay đổi trạng thái OSD; nếu Ceph tự đánh dấu nhiều OSD out và báo DEVICE_HEALTH_TOOMANY, ưu tiên kiểm tra từng thiết bị/PG và không ép in/start hàng loạt. Không wipe thiết bị hoặc destroy OSD trước khi xác định đúng serial/OSD và xác nhận an toàn dữ liệu.

## Nguồn tham khảo

- [Ceph: Device management and health monitoring](https://docs.ceph.com/en/reef/rados/operations/devices/)
- [Ceph: Health checks](https://docs.ceph.com/en/reef/rados/operations/health-checks/)

<!-- từ khóa: ceph osd devicehealth device health device_health_toomany disk sắp hỏng disk failure predicted failure SMART health metrics tuổi thọ đĩa out -->
