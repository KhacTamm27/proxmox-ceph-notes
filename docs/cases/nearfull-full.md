# Ceph nearfull / full / pool đầy

[← Mục lục](../../README.md)

**Triệu chứng:** HEALTH_WARN "N osd(s) nearfull", HEALTH_ERR "full osd(s)", client không ghi được, backfill dừng.

**Nguyên nhân hay gặp:** Dung lượng toàn cluster cạn, hoặc dữ liệu phân bố lệch làm một vài OSD đầy trước.

## Các bước xử lý

1. Xem dung lượng tổng và theo pool

```bash
ceph df
ceph health detail
```

2. Tìm OSD hoặc host đầy nhất, xem độ lệch

```bash
ceph osd df tree
ceph osd utilization
```

3. Nếu chỉ lệch: giảm tải OSD đầy

```bash
ceph osd reweight-by-utilization
ceph osd reweight <osd-id> 0.9
```

4. Giải phóng chỗ: xóa dữ liệu không cần hoặc thêm OSD, rồi theo dõi

```bash
ceph -w
```

5. Khẩn cấp để mở ghi lại (chỉ tạm thời, trả về mặc định sau khi xử lý xong)

```bash
ceph osd set-full-ratio 0.95
```

## Lưu ý

Không nâng ngưỡng full quá cao. Khi OSD chạm 100% có thể không khởi động được. Cluster nên giữ dưới khoảng 80% dung lượng.

<!-- từ khóa: ceph nearfull full đầy disk dung lượng backfillfull osd đầy -->
