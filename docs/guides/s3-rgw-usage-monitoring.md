# Giám sát S3 User Ops bằng Ceph RADOSGW Usage Exporter

> **Phạm vi:** theo dõi số thao tác (ops), băng thông và tỉ lệ lỗi của từng S3 user / bucket trên Ceph RGW, hiển thị bằng Grafana, cảnh báo bằng Prometheus.
> **Trạng thái:** đã dựng và có metric thật trên môi trường lab (S3-GW + VM monitor). Bộ script tự động đã được review và kiểm thử với file cấu hình giả lập; lần chạy đầu trên lab cần đối chiếu kết quả (mục 1.5). Ngày cập nhật: 2026-10-24.
> **Bộ file đi kèm** (thư mục [`tools/s3-rgw-usage/`](../../tools/s3-rgw-usage/)): `s3gw-prepare.sh`, `monitor-deploy.sh`, `rgw-usage-alerts.yml`, `rgw-usage-dashboard.json`.
> **Lưu ý:** IP, tên user và đường dẫn trong bài là của môi trường lab, thay bằng giá trị của môi trường khác khi áp dụng.

---

## 0. Tóm tắt nhanh

| Câu hỏi | Trả lời |
|---|---|
| Làm gì? | Thêm giám sát **ops/s theo S3 user** (và theo bucket, theo loại thao tác, băng thông, tỉ lệ lỗi) cho S3 Gateway |
| Dùng gì? | **Ceph RADOSGW Usage Exporter** → Prometheus → Grafana |
| Exporter lấy số liệu từ đâu? | Gọi **Admin Ops API** (`/admin`) của RGW, đọc **usage log** do RGW ghi lại |
| Cài ở đâu? | Exporter chạy bằng Docker trên **VM monitor**, không cần cài gì lên node RGW (ngoài việc bật usage log và tạo user) |
| Mất bao lâu? | Chạy 2 script, khoảng 10 phút |
| Độ trễ số liệu? | Vài phút (RGW ghi usage log theo lô), không realtime |

Phần này **bổ sung** cho hai hướng giám sát đã có (Nginx VTS và Loki + Promtail). Ba hướng bổ trợ nhau, không thay thế nhau:

| Hướng | Trả lời được câu hỏi nào |
|---|---|
| Nginx VTS (xem bài [S3 qua NGINX reverse proxy và cache](s3-nginx-cache-proxy.md)) | Cache HIT/MISS/BYPASS, 4xx/5xx, số session |
| Loki + Promtail | URI/URL nào bị MISS/BYPASS |
| **RGW Usage Exporter (tài liệu này)** | **S3 user / bucket nào đang dùng bao nhiêu ops/s, băng thông, lỗi** |

---

## 1. Mô hình test hiện tại

### 1.1 Sơ đồ kết nối

```
S3 client (S3 Browser, aws cli)
        │  S3 API
        ▼
S3-GW  192.168.69.190:8080   (radosgw, ghi usage log)
        ▲
        │  Admin Ops API (/admin), ký bằng khóa của user usage-exporter
        │
VM Tam-K3S (VM monitor)  192.168.69.172
  ├─ rgw-usage-exporter   :9242   (docker run, file env: /opt/rgw-exporter/env)
  ├─ Prometheus           :9090   (scrape exporter mỗi 60s, nạp luật cảnh báo)
  ├─ Grafana              :3000   (datasource Prometheus, dashboard "S3 RGW - User Ops")
  └─ node-exporter                (theo dõi chính VM monitor)
```

### 1.2 Bảng thành phần

| Thành phần | Vị trí | Cổng | Vai trò |
|---|---|---|---|
| radosgw (S3-GW) | 192.168.69.190 | 8080 | Nhận S3 request, ghi usage log, cung cấp Admin Ops API |
| rgw-usage-exporter | VM monitor 192.168.69.172 | 9242 | Hỏi RGW, đổi dữ liệu usage thành metric Prometheus |
| Prometheus | VM monitor | 9090 | Lấy metric từ exporter mỗi 60s, đánh giá luật cảnh báo |
| Grafana | VM monitor | 3000 | Dashboard |
| node-exporter | VM monitor | (nội bộ) | Giám sát tài nguyên của VM monitor |

### 1.3 User S3 trong mô hình test

| User | Mục đích | Quyền |
|---|---|---|
| `usage-exporter` | Chỉ để Exporter đọc thống kê | caps: `buckets=read; users=read; usage=read; metadata=read; info=read` (không có quyền ghi, không đọc được dữ liệu object) |
| `test-ops` | Tạo lưu lượng thử bằng S3 Browser / aws cli | User S3 thường |
| `khactamms3`, `KH_KhacTam`, `uploaduser`, `aws_cache` | User có sẵn của hệ thống | Không đổi |

### 1.4 Đường dẫn quan trọng

| Đường dẫn | Nội dung |
|---|---|
| `/opt/monitoring/docker-compose.yml` | Stack Prometheus + Grafana + node-exporter |
| `/opt/monitoring/prometheus/prometheus.yml` | Cấu hình Prometheus (có job `rgw-usage`) |
| `/opt/monitoring/prometheus/rules/rgw-usage-alerts.yml` | Luật cảnh báo |
| `/opt/monitoring/grafana/provisioning/datasources/prometheus.yml` | Datasource Prometheus cho Grafana |
| `/opt/rgw-exporter/env` | Cấu hình + khóa của Exporter (quyền 600) |

### 1.5 Quá trình dựng lab (đã làm) và hiện trạng

Các bước đã làm tay trên lab, theo thứ tự:

1. Dựng VM monitor bằng `setup-monitoring.sh`: cài Docker, tạo thư mục và cấu hình, chạy Prometheus, Grafana, node-exporter bằng `docker compose`.
2. Sửa `prometheus.yml`: job `rgw-usage` bị thụt **3** dấu cách (các job khác là 2) nên Prometheus báo `did not find expected '-' indicator`.
3. Kiểm tra RGW: trên S3-GW, `netstat`/`ss` thấy `radosgw` nghe cổng 8080; từ VM monitor `telnet 192.168.69.190 8080` thông.
4. Chạy `rgw-usage-exporter` trên **VM monitor** (không chạy trên S3-GW), đọc RGW qua mạng.
5. Sửa `RADOSGW_SERVER`: container từng được tạo với `http://http://192.168.69.190:8080/` nên báo `Failed to resolve 'http'`. Xóa container, sửa file env, tạo lại bằng `--env-file`; log hiện `Polling http://192.168.69.190:8080`.
6. Có metric thật tại `:9242/metrics`: `radosgw_usage_ops_total`, `successful_ops_total`, `sent_bytes_total`, `received_bytes_total`, nhãn `owner`, `bucket`, `category`, `store`.
7. Chốt các truy vấn dashboard theo nhãn **`owner`** (không phải `user`).

Hiện trạng cần xác nhận khi chạy lại:

| Mục | Trạng thái | Cách xác nhận |
|---|---|---|
| Target của job `rgw-usage` | Từng để `192.168.69.190:9242` (sai, đó là IP RGW). Phải là `192.168.69.172:9242` | `http://192.168.69.172:9090/targets` thấy `rgw-usage` **UP**. `monitor-deploy.sh` cảnh báo nếu target vẫn sai (script không tự sửa job đã có) |
| Khóa của `usage-exporter` | Khóa cũ đã xuất hiện trong chat | Lab thì giữ được; xoay khóa theo mục 9 trước khi dùng cho môi trường khác |
| Mật khẩu Grafana | Có thể vẫn là mặc định `ChangeMe@123` | Đổi theo mục 8 |
| Kênh thông báo cảnh báo | Chưa có | Mục 12 |

---

## 2. Cơ chế và luồng hoạt động

### 2.1 Luồng chạy từng bước

1. Client gửi S3 request tới RGW (tạo bucket, upload, list...).
2. RGW xử lý request và **ghi thống kê vào usage log** (gom theo user, bucket, loại thao tác; ghi theo lô nên có độ trễ).
3. Prometheus cứ **60 giây** lại truy cập `http://192.168.69.172:9242/metrics`.
4. Mỗi lần được hỏi, Exporter gọi **Admin Ops API** của RGW (đường dẫn `/admin`), ký bằng khóa của `usage-exporter`, đọc thống kê.
5. Exporter trả về metric dạng `radosgw_usage_*{owner, bucket, category, store}`.
6. Prometheus lưu metric thành time-series (mặc định giữ 30 ngày) và đánh giá luật cảnh báo.
7. Grafana truy vấn Prometheus, dùng `rate()` để ra ops/s và vẽ dashboard.

### 2.2 Metric và nhãn

| Metric | Ý nghĩa |
|---|---|
| `radosgw_usage_ops_total` | Số thao tác |
| `radosgw_usage_successful_ops_total` | Số thao tác thành công |
| `radosgw_usage_sent_bytes_total` | Byte RGW gửi ra (download) |
| `radosgw_usage_received_bytes_total` | Byte RGW nhận vào (upload) |

| Nhãn | Ý nghĩa | Ví dụ |
|---|---|---|
| `owner` | S3 user sở hữu (**dùng nhãn này, không phải `user`**) | `test-ops`, `anonymous` |
| `bucket` | Bucket | `new-bucket-f9d11201`; `-` hoặc rỗng nếu thao tác không thuộc bucket nào |
| `category` | Loại thao tác | `put_obj`, `list_bucket`, `create_bucket`, `init_multipart`, `get_bucket_object_lock` |
| `store` | Tên store của RGW | `default` |

### 2.3 Độ trễ cần nhớ

- RGW ghi usage log theo lô → dữ liệu xuất hiện sau **vài chục giây đến vài phút**.
- `rate()` cần **ít nhất 2 lần scrape** (khoảng 2 phút) mới ra số.
- Vì vậy dashboard này dùng để **theo dõi xu hướng và phát hiện bất thường**, không dùng để xem từng request theo thời gian thực. Cần xem từng request thì dùng hướng Loki + Promtail.

---

## 3. Chuẩn bị

| # | Cần có | Cách kiểm tra |
|---|---|---|
| 1 | Quyền root trên S3-GW (node có `radosgw-admin`) | `radosgw-admin user list` chạy được |
| 2 | VM monitor đã dựng stack bằng `setup-monitoring.sh` (có `/opt/monitoring`) | `docker ps` thấy prometheus, grafana |
| 3 | Docker trên VM monitor | `docker --version` |
| 4 | VM monitor với tới được RGW | `curl -i http://192.168.69.190:8080` trả HTTP 200 và XML `ListAllMyBucketsResult` |
| 5 | Mật khẩu Grafana (user `admin`) | Đăng nhập được `http://192.168.69.172:3000` |
| 6 | 4 file của bộ script đặt cùng một thư mục trên mỗi máy cần chạy | `ls` |

Máy nào chạy script nào:

| Script | Chạy trên | Cần các file |
|---|---|---|
| `s3gw-prepare.sh` | S3-GW | chỉ chính nó |
| `monitor-deploy.sh` | VM monitor | `rgw-usage-alerts.yml`, `rgw-usage-dashboard.json` đặt cạnh script |

---

## 4. Triển khai tự động bằng script

### 4.1 Bước 1: chuẩn bị phía RGW (chạy trên S3-GW)

```bash
bash s3gw-prepare.sh --with-test-user
```

Script làm:

1. Kiểm tra **usage log** đã có dữ liệu chưa. Nếu chưa có dữ liệu nhưng `rgw_enable_usage_log` đã là `true` thì chỉ là chưa có lưu lượng: script **không** restart RGW. Nếu chưa bật thì bật và hỏi trước khi restart RGW (chạy không có terminal thì mặc định không restart).
2. Tạo user `usage-exporter` với đúng 5 quyền đọc. Nếu user đã tồn tại thì bổ sung quyền còn thiếu và **kiểm tra lại đủ 5 quyền**.
3. Ghi file `/root/rgw-exporter.env` (quyền 600) gồm địa chỉ RGW và khóa. **Khóa không in ra màn hình.**
4. Với `--with-test-user`: tạo user `test-ops`, khóa nằm ở `/root/test-ops-keys.txt` (quyền 600).

Tùy chọn: `--rgw-url http://IP:CỔNG` (nếu script không tự dò đúng), `-y` (tự đồng ý restart RGW).

Chép file env sang VM monitor:

```bash
scp /root/rgw-exporter.env root@192.168.69.172:/tmp/rgw-exporter.env
```

### 4.2 Bước 2: triển khai phía monitor (chạy trên VM monitor)

```bash
GRAFANA_PASSWORD='mat-khau-grafana' \
bash monitor-deploy.sh install --env-file /tmp/rgw-exporter.env --site lab
```

Script làm theo thứ tự:

1. **Kiểm tra file env:** bắt lỗi `http://http://`, thiếu khóa, và thử kết nối tới RGW.
2. **Tạo lại container** `rgw-usage-exporter` (xóa cũ, tạo mới với `--env-file`, `--restart always`), chờ đến khi có metric.
3. **Sửa cấu hình Prometheus** (có backup trước khi sửa):
   - `prometheus.yml`: thêm `rule_files` và job `rgw-usage` (target là **IP của VM**, không dùng `localhost`, xem mục 7.6).
   - `docker-compose.yml`: thêm volume `./prometheus/rules`.
4. Chép luật cảnh báo, chạy `docker compose up -d`, kiểm tra bằng `promtool`, rồi reload Prometheus. **Nếu `promtool` báo lỗi thì tự khôi phục file cũ.**
5. **Import dashboard** vào Grafana qua API (cần `GRAFANA_PASSWORD`; không có thì bỏ qua và báo cách import tay).
6. **Chạy bộ kiểm tra cuối** và in kết quả đạt/lỗi.

Đặc điểm: **chạy lại nhiều lần được** (không nhân đôi job, không thêm trùng volume). Dòng thêm vào `prometheus.yml` và `docker-compose.yml` dùng đúng thụt lề của file đang có. Nếu job `rgw-usage` đã có từ trước (sửa tay), script **giữ nguyên** job đó và chỉ cảnh báo khi target khác `IP-VM:9242`. Nếu `docker compose up` hoặc `promtool` lỗi, script khôi phục cả hai file từ bản backup. File env bị CRLF (soạn trên Windows) hoặc có giá trị trong dấu nháy sẽ bị chặn ngay ở bước kiểm tra. Mỗi lần chạy sẽ tạo lại container Exporter (gián đoạn vài giây, không ảnh hưởng dịch vụ S3).

Các lệnh con khác:

```bash
bash monitor-deploy.sh check                       # chỉ kiểm tra, không đổi gì
GRAFANA_PASSWORD='***' bash monitor-deploy.sh import-dashboard   # nhập lại dashboard
```

### 4.3 Bước 3: tạo lưu lượng thử và xác nhận

1. Mở S3 Browser, thêm tài khoản bằng khóa trong `/root/test-ops-keys.txt` (endpoint `http://192.168.69.190:8080`).
2. Tạo bucket, upload vài file, download một file, bấm Refresh vài lần.
3. Đợi 2 đến 3 phút.
4. Kiểm tra từng tầng:

| Tầng | Lệnh / nơi xem | Kết quả đạt |
|---|---|---|
| RGW | `radosgw-admin usage show --uid=test-ops` (trên S3-GW) | Có `ops`, `successful_ops` lớn hơn 0 |
| Exporter | `curl -s localhost:9242/metrics \| grep radosgw_usage_ops_total` | Có dòng với `owner="test-ops"` |
| Prometheus | `http://192.168.69.172:9090/targets` | `rgw-usage` ở trạng thái **UP** |
| Prometheus | `http://192.168.69.172:9090/alerts` | Nhóm `rgw-usage`, 3 luật, trạng thái Inactive |
| Grafana | `http://192.168.69.172:3000/d/rgw-usage-ops` | Biểu đồ ops/s có đường của `test-ops` |

### 4.4 Rollback

Script luôn tạo bản backup `*.bak-<thời gian>` trước khi sửa:

```bash
ls /opt/monitoring/*.bak-* /opt/monitoring/prometheus/*.bak-*
cp /opt/monitoring/prometheus/prometheus.yml.bak-<thời gian> /opt/monitoring/prometheus/prometheus.yml
cp /opt/monitoring/docker-compose.yml.bak-<thời gian>       /opt/monitoring/docker-compose.yml
cd /opt/monitoring && docker compose up -d
docker rm -f rgw-usage-exporter                    # gỡ Exporter nếu cần
```

---

## 5. Triển khai thủ công (để hiểu từng bước)

Dùng khi muốn làm tay hoặc script gặp lỗi. Kết quả giống hệt script.

**5.1 Bật usage log (nếu chưa có dữ liệu)**

```bash
ceph config set client.rgw rgw_enable_usage_log true
systemctl restart ceph-radosgw@rgw.S3GW.service
```

**5.2 Tạo user Exporter (chỉ đọc)**

```bash
radosgw-admin user create --uid=usage-exporter --display-name="Usage Exporter" \
  --caps="buckets=read;users=read;usage=read;metadata=read;info=read"
```

Lưu `access_key` và `secret_key` ở kết quả trả về.

**5.3 File env của Exporter** (`/opt/rgw-exporter/env`, `chmod 600`)

```
RADOSGW_SERVER=http://192.168.69.190:8080
ADMIN_ENTRY=admin
ACCESS_KEY=<access_key>
SECRET_KEY=<secret_key>
VIRTUAL_PORT=9242
STORE=default
```

Lưu ý: giá trị `RADOSGW_SERVER` chỉ có **một** `http://`, không có dấu `/` thừa, không khoảng trắng.

**5.4 Chạy Exporter**

```bash
docker run -d --name rgw-usage-exporter --restart always -p 9242:9242 \
  --env-file /opt/rgw-exporter/env blemmenes/radosgw_usage_exporter
```

**5.5 Khai báo Prometheus** (`/opt/monitoring/prometheus/prometheus.yml`, **thụt lề 2 dấu cách**, giống các job khác)

```yaml
rule_files:
  - /etc/prometheus/rules/*.yml

scrape_configs:
  # ... các job có sẵn ...
  - job_name: rgw-usage
    scrape_interval: 60s
    static_configs:
      - targets: ['192.168.69.172:9242']
        labels:
          site: 'lab'
```

Trong `docker-compose.yml`, mục `prometheus` → `volumes`, thêm: `- ./prometheus/rules:/etc/prometheus/rules:ro`, rồi:

```bash
cd /opt/monitoring && docker compose up -d
docker exec prometheus promtool check config /etc/prometheus/prometheus.yml
curl -X POST http://localhost:9090/-/reload
```

**5.6 Dashboard:** Grafana → Dashboards → New → Import → chọn `rgw-usage-dashboard.json`.

---

## 6. Dashboard và cảnh báo

### 6.1 Dashboard "S3 RGW - User Ops" (uid `rgw-usage-ops`)

Đầu trang có 3 ô lọc: **Datasource**, **S3 user** (`owner`), **Bucket** (mặc định All).

| Panel | Truy vấn (rút gọn, `F` = bộ lọc owner/bucket) |
|---|---|
| Tổng ops/s | `sum(rate(radosgw_usage_ops_total{F}[5m]))` |
| Tỉ lệ lỗi (5 phút) | `clamp_min(clamp_max(1 - sum(rate(..successful_ops..)) / sum(rate(..ops..)), 1), 0)` |
| Băng thông ra / vào | `sum(rate(radosgw_usage_sent_bytes_total{F}[5m]))` / `...received_bytes_total...` |
| ops/s theo S3 user | `sum by (owner) (rate(radosgw_usage_ops_total{F}[5m]))` |
| Top 10 user | `topk(10, sum by (owner) (rate(radosgw_usage_ops_total{F}[5m])))` |
| ops/s theo bucket | `sum by (bucket) (rate(radosgw_usage_ops_total{F}[5m]))` |
| ops/s theo loại thao tác | `sum by (category) (rate(radosgw_usage_ops_total{F}[5m]))` |
| Tỉ lệ lỗi theo user | như trên, `by (owner)` |
| Băng thông ra / vào theo user | `sum by (owner) (rate(..bytes_total{F}[5m]))` |

Hai panel tỉ lệ lỗi **loại trừ** `category="get_bucket_object_lock"` (lỗi "giả" do S3 client hỏi object lock, xem mục 7.4) và bị giới hạn trong khoảng 0 đến 100%.

### 6.2 Luật cảnh báo (`rgw-usage-alerts.yml`)

| Luật | Điều kiện | Giữ trong | Mức |
|---|---|---|---|
| `RGWUsageExporterDown` | `up{job="rgw-usage"} == 0` | 2 phút | critical |
| `RGWUserErrorRateHigh` | Tỉ lệ lỗi của một user trên 10% **và** lưu lượng trên 0.05 ops/s | 10 phút | warning |
| `RGWUserOpsSpike` | ops/s của một user trên 1 **và** gấp hơn 3 lần so với 1 giờ trước | 5 phút | warning |

Hai luật sau có **ngưỡng lưu lượng tối thiểu** để lúc ít request không báo nhầm. Các ngưỡng là giá trị khởi điểm, cần chỉnh theo thực tế sau vài ngày quan sát.

**Hiện chưa có kênh thông báo.** Luật chỉ hiện ở `http://192.168.69.172:9090/alerts`. Xem mục 12.

---

## 7. Cần double check

### 7.1 Kiểm tra kiểu metric
Exporter đọc **tổng tích lũy** từ usage log mỗi lần được hỏi; chưa xác nhận bản đang chạy khai báo metric là *counter* hay *gauge*. Dù là loại nào, khi tổng **giảm** (xóa user/bucket, `usage trim`) thì `rate()` coi là bộ đếm reset và đồ thị có thể nhảy một điểm. Kiểm tra bản đang dùng:

```bash
curl -s localhost:9242/metrics | grep '^# TYPE radosgw_usage'
```

### 7.2 Độ trễ
Số liệu trễ vài phút (mục 2.3). Đừng dùng cảnh báo cần phản ứng trong vài chục giây.

### 7.3 `owner="anonymous"`
Là request không ký (ví dụ mở thẳng URL trên trình duyệt). Không phải lỗi. Nếu nhiều quá và gây nhiễu, loại ra trong dashboard/luật bằng `owner!="anonymous"`.

### 7.4 `get_bucket_object_lock` luôn "thất bại"
S3 Browser (và một số client) hỏi trạng thái object lock; bucket chưa cấu hình thì RGW trả lỗi, RGW tính là một thao tác không thành công. Vô hại, nên đã loại khỏi các panel và luật tỉ lệ lỗi. Nếu có client khác sinh ra "lỗi giả" tương tự, thêm vào bộ loại trừ `category!~"a|b"`.

### 7.5 Panel tỉ lệ lỗi hiện trục 0% đến 10000%
Khi panel `percentunit` **không có dữ liệu**, Grafana dùng trục mặc định 0 đến 100 rồi hiển thị ×100%, nên thấy 10000%. Bản dashboard hiện tại đã khóa trục 0 đến 100%. Nếu panel vẫn trống, kiểm tra theo thứ tự trong Prometheus (`/query`):

1. `radosgw_usage_successful_ops_total` có dữ liệu không?
2. `sum by (owner) (rate(radosgw_usage_successful_ops_total[5m]))` có ra không?
3. `sum by (owner) (rate(radosgw_usage_ops_total[5m]))` có ra không?

Phép chia chỉ có kết quả khi cả hai vế cùng có dữ liệu cho cùng `owner`. Khi chưa có thao tác nào (chia 0/0) panel cũng trống, đó là bình thường.

### 7.6 Prometheus chạy trong container, không dùng `localhost`
Target phải là **IP của VM** (`192.168.69.172:9242`). Nếu để `localhost:9242` thì Prometheus tìm Exporter *bên trong chính container Prometheus* và target sẽ DOWN.

### 7.7 Exporter phải trỏ **thẳng RGW**
Không trỏ qua Nginx cache. Admin API không nên đi qua cache, và cache có thể làm sai lệch số liệu.

### 7.8 `radosgw-admin usage trim`
Xóa usage log, bộ đếm về 0, đồ thị rơi. Hiện tượng bình thường. Usage log lớn dần theo thời gian (nằm trong pool log của RGW), nên cần có kế hoạch trim định kỳ cho môi trường thật, và thông báo cho người xem dashboard.

### 7.9 Nhãn `bucket` bằng `-` hoặc rỗng
Là các thao tác không thuộc bucket nào (ví dụ liệt kê danh sách bucket). Không phải lỗi.

### 7.10 Số Exporter cần
Theo hiểu biết hiện tại, usage log là của cả zone/cluster nên **một Exporter trỏ vào một RGW** là đủ cho cả cụm RGW cùng zone. Khi triển khai thật nên xác nhận lại bằng cách so sánh với `radosgw-admin usage show`.

### 7.11 Docker bỏ qua tường lửa ufw
Cổng publish bằng `docker run -p 9242:9242` được Docker mở trực tiếp trong iptables, **ufw không chặn được**. Muốn giới hạn chỉ mạng quản trị truy cập, dùng chain `DOCKER-USER`, ví dụ:

```bash
iptables -I DOCKER-USER -p tcp --dport 9242 ! -s 192.168.69.0/24 -j DROP
```

Lệnh trên không tự lưu sau reboot; dùng `iptables-persistent` hoặc cơ chế tường lửa đang dùng trên VM.

### 7.12 `up == 1` chỉ có nghĩa là Exporter còn trả lời
Luật `RGWUsageExporterDown` dựa trên `up`, tức là Prometheus gọi được Exporter. Nếu Exporter vẫn chạy nhưng **không gọi được RGW** (sai khóa, RGW down), target vẫn có thể UP trong khi số liệu đứng yên. Khi nghi ngờ, xem `docker logs --tail 30 rgw-usage-exporter` (403, timeout) và so với `radosgw-admin usage show`.

### 7.13 Luật "ops tăng đột biến" không bắt user mới
`RGWUserOpsSpike` so với 1 giờ trước. User **mới xuất hiện** (1 giờ trước chưa có series) không có giá trị để so nên luật không kích hoạt. Nếu cần, thêm luật theo ngưỡng tuyệt đối (ví dụ `RGWBucketOpsHigh` ở mục 10.1).

---

## 8. Lỗi thường gặp và cách xử lý

| Hiện tượng | Nguyên nhân | Cách xử lý |
|---|---|---|
| Prometheus: `did not find expected '-' indicator` | Job `rgw-usage` thụt lề sai (3 dấu cách) trong YAML | Căn lại **2 dấu cách** như các job khác |
| Exporter: `Failed to resolve 'http'` | `RADOSGW_SERVER` bị thành `http://http://...` | Sửa file env, **tạo lại container** (`docker rm -f` rồi `docker run`) |
| `docker compose` báo không có file | Exporter chạy bằng `docker run`, không nằm trong compose | Dùng `docker rm -f rgw-usage-exporter` rồi `docker run ... --env-file` |
| Sửa file env nhưng không có tác dụng | Biến môi trường chỉ nạp lúc **tạo** container, `restart` không đủ | Tạo lại container (hoặc chạy lại `monitor-deploy.sh install`) |
| Log Exporter báo 403 / AccessDenied | Sai khóa hoặc user Exporter thiếu quyền | `radosgw-admin user info --uid=usage-exporter` kiểm tra đủ 5 caps; chạy lại `s3gw-prepare.sh` |
| Log báo không kết nối được | Sai IP/cổng RGW hoặc bị chặn mạng | `curl -i http://IP-RGW:CỔNG` từ VM monitor |
| `/metrics` không có `radosgw_usage_*` | Usage log chưa bật hoặc chưa có lưu lượng nào | `radosgw-admin usage show`; tạo lưu lượng thử, đợi vài phút |
| Target `rgw-usage` DOWN | Container không chạy, sai IP (dùng `localhost`), tường lửa cổng 9242 | `docker ps`, `curl localhost:9242/metrics`, kiểm tra target trong `prometheus.yml` |
| Tab Alerts không có nhóm `rgw-usage` | Thiếu volume rules hoặc `rule_files` | `docker exec prometheus ls /etc/prometheus/rules`; kiểm tra mục 5.5 |
| Reload báo lỗi | Prometheus không bật `--web.enable-lifecycle` | `docker restart prometheus` |
| Dashboard "No data" | Chưa đủ 2 lần scrape, khoảng thời gian quá ngắn, hoặc biến lọc sai | Chọn "Last 1 hour", để biến lọc là All, đợi 2 đến 3 phút |
| Không đăng nhập được Grafana | Mật khẩu đã đổi, hoặc volume Grafana cũ giữ mật khẩu cũ | `docker exec -it grafana grafana cli admin reset-admin-password <mật-khẩu-mới>` |
| Script báo `scrape_configs không phải mục cuối file` | `prometheus.yml` có mục khác sau `scrape_configs` | Thêm job `rgw-usage` bằng tay theo mục 5.5 (script đã khôi phục file nguyên vẹn) |
| Script cảnh báo `Job rgw-usage đã có nhưng target là ...` | Job sửa tay từ trước, target trỏ sai (ví dụ IP của RGW) | Sửa `targets` thành `IP-VM-monitor:9242`, reload, kiểm tra `/targets` |
| Script báo file env có CRLF hoặc dấu nháy | File env soạn trên Windows, hoặc viết `KEY="giá trị"` | `sed -i 's/\r$//' <file>`, bỏ dấu nháy, chạy lại |
| `s3gw-prepare.sh` báo user có nhiều khóa S3 | Đang xoay khóa, user có cả khóa cũ và mới | Chạy lại với `EXPORTER_ACCESS_KEY=<khóa mới>` |
| Chạy script báo `$'\r': command not found` | Script bị đổi sang CRLF khi tải hoặc clone trên Windows | `sed -i 's/\r$//' *.sh` (repo đã có `.gitattributes` giữ LF cho file `.sh`) |

---

## 9. Các trường hợp thay đổi, thêm bớt

| Nhu cầu | Cách làm |
|---|---|
| Đổi IP/cổng RGW | Sửa `RADOSGW_SERVER` trong `/opt/rgw-exporter/env`, chạy lại `bash monitor-deploy.sh install` |
| Đổi (xoay) khóa Exporter | Trên S3-GW: `radosgw-admin key create --uid=usage-exporter --key-type=s3 --gen-access-key --gen-secret`, chạy lại `EXPORTER_ACCESS_KEY=<khóa-mới> bash s3gw-prepare.sh` (hoặc sửa tay file env), tạo lại container bằng `monitor-deploy.sh install`, xác nhận có metric, sau đó mới xóa khóa cũ: `radosgw-admin key rm --uid=usage-exporter --key-type=s3 --access-key=<khóa-cũ>` |
| Đổi IP VM monitor | Sửa `targets` của job `rgw-usage` trong `prometheus.yml`, reload |
| Đổi nhãn site | Sửa `labels.site`, reload (dữ liệu cũ vẫn mang nhãn cũ đến hết thời gian lưu) |
| Thêm site/cụm RGW khác | Chạy thêm một Exporter trỏ vào RGW của site đó (khác tên container, cổng, file env), rồi thêm một khối `targets` mới với nhãn `site` khác vào **cùng job** `rgw-usage`. Script không tự làm bước này, cần sửa tay |
| Đổi tần suất lấy số liệu | Sửa `scrape_interval` của job (không nên dưới 60s do độ trễ usage log) |
| Đổi thời gian lưu dữ liệu | Sửa `PROM_RETENTION` (mặc định `30d`) trong `docker-compose.yml`: `--storage.tsdb.retention.time=`, rồi `docker compose up -d` |
| Cố định phiên bản Exporter | `EXPORTER_IMAGE=blemmenes/radosgw_usage_exporter:<tag> bash monitor-deploy.sh install`. Nên cố định phiên bản khi lên production, tránh `latest` tự đổi |
| Đổi mật khẩu Grafana | Lệnh `grafana cli admin reset-admin-password` ở mục 8, hoặc đổi trong giao diện |
| Gỡ giám sát | `docker rm -f rgw-usage-exporter`, xóa job `rgw-usage` và `rule_files`, xóa file rules, `docker compose up -d`, xóa dashboard trong Grafana. Có thể xóa user: `radosgw-admin user rm --uid=usage-exporter` |

---

## 10. Tùy biến: thêm rule, sửa dashboard

### 10.1 Thêm luật cảnh báo

**Quan trọng:** `monitor-deploy.sh` **ghi đè** `rgw-usage-alerts.yml` bằng file cạnh script. Vì vậy:
- Muốn sửa 3 luật mặc định: sửa **file nguồn** (cạnh script) rồi chạy lại `install`.
- Muốn thêm luật riêng: tạo **file khác**, ví dụ `rgw-usage-custom.yml`, đặt vào `/opt/monitoring/prometheus/rules/`. Script không đụng tới file này (mẫu `rule_files` đã nạp mọi file `*.yml` trong thư mục).

Quy trình:

```bash
nano /opt/monitoring/prometheus/rules/rgw-usage-custom.yml
docker exec prometheus promtool check rules /etc/prometheus/rules/rgw-usage-custom.yml
curl -X POST http://localhost:9090/-/reload
```

Ví dụ nội dung:

```yaml
groups:
  - name: rgw-usage-custom
    rules:
      # Một user tải xuống quá 50 MB/s trong 10 phút
      - alert: RGWUserEgressHigh
        expr: sum by (owner) (rate(radosgw_usage_sent_bytes_total[5m])) > 50 * 1024 * 1024
        for: 10m
        labels: { severity: warning }
        annotations:
          summary: "User {{ $labels.owner }} đang tải xuống quá nhiều"
          description: "Băng thông ra {{ $value | humanize1024 }}B/s."

      # User quan trọng không có hoạt động nào trong 1 giờ
      - alert: RGWKeyUserInactive
        expr: sum(increase(radosgw_usage_ops_total{owner="khactamms3"}[1h])) == 0
        for: 5m
        labels: { severity: info }
        annotations:
          summary: "User khactamms3 không có thao tác nào trong 1 giờ"

      # Một bucket có ops/s cao bất thường
      - alert: RGWBucketOpsHigh
        expr: sum by (bucket) (rate(radosgw_usage_ops_total{bucket!~"-|"}[5m])) > 20
        for: 10m
        labels: { severity: warning }
        annotations:
          summary: "Bucket {{ $labels.bucket }} có {{ $value | humanize }} ops/s"
```

Mẹo: thử câu truy vấn ở `http://192.168.69.172:9090/query` trước, thấy kết quả hợp lý rồi mới đưa vào luật. Đặt `for:` đủ dài để tránh báo nhầm do dữ liệu trễ theo lô.

### 10.2 Sửa dashboard

1. Trong Grafana: mở dashboard, bấm **Edit**, thêm/sửa panel (ví dụ thêm panel ops/s theo `category` cho riêng một user).
2. **Save**.
3. Muốn giữ bản sửa trong git: **Share → Export → Save to file**, thay file `rgw-usage-dashboard.json`.
4. Cần nạp lại ở máy khác: `GRAFANA_PASSWORD='***' bash monitor-deploy.sh import-dashboard`.

Lưu ý: `import-dashboard` **ghi đè** dashboard cùng `uid`. Bản sửa trong giao diện mà **chưa export** sẽ mất khi import lại.

Một số chỉnh sửa hay dùng:

| Muốn | Làm |
|---|---|
| Loại user `anonymous` | Thêm `owner!="anonymous"` vào bộ lọc của các truy vấn |
| Thêm biến lọc `site` | Dashboard settings → Variables → New, truy vấn `label_values(radosgw_usage_ops_total, site)`, rồi thêm `site=~"$site"` vào các truy vấn |
| Đổi khoảng thời gian tính tốc độ | Đổi `[5m]` thành `[10m]` (mượt hơn nhưng chậm phản ứng hơn) |
| Hiển thị tên thân thiện cho user | Dùng *Overrides* trong panel hoặc *Value mappings* |

---

## 11. Bảo mật

- File env chỉ cho root đọc: `chmod 600 /opt/rgw-exporter/env`. Xóa bản tạm sau khi chép: `shred -u /tmp/rgw-exporter.env`.
- User Exporter **chỉ có quyền đọc**. Không dùng user quản trị toàn quyền cho Exporter.
- **Không dán khóa vào chat, ticket, wiki.** Nếu lỡ lộ, xoay khóa ngay (mục 9).
- Đổi mật khẩu Grafana mặc định (`ChangeMe@123` trong `setup-monitoring.sh`) sau khi cài.
- Cổng `9242` (Exporter) chỉ cần cho Prometheus truy cập; giới hạn bằng chain `DOCKER-USER` vì ufw không chặn cổng Docker publish (mục 7.11). Cổng Prometheus/Grafana chỉ mở cho mạng quản trị.
- Admin Ops API (`/admin`) của RGW chỉ nên với tới được từ VM monitor, không công khai ra Internet.

---

## 12. Lên production

1. **Mỗi site một Exporter**, đặt gần RGW của site đó, trỏ **thẳng RGW** (không qua Nginx cache). Thêm nhãn `site` (FPT-HCM, FPT-HN...) vào từng target.
2. Cố định phiên bản image Exporter (mục 9).
3. Dùng mật khẩu và khóa riêng cho từng môi trường, không dùng lại khóa của lab.
4. Xây dựng chính sách **trim usage log** định kỳ và thống nhất thời điểm với người dùng dashboard (mục 7.8).
5. Thiết lập **kênh thông báo** (Telegram hoặc email) cho cảnh báo. Có hai cách:
   - Thêm **Alertmanager** vào `docker-compose.yml` và khai báo `alerting:` trong `prometheus.yml`.
   - Hoặc tạo luật cảnh báo trực tiếp trong **Grafana Alerting** với Contact point.
6. Điều chỉnh ngưỡng cảnh báo sau 1 đến 2 tuần quan sát số liệu thật.
7. Ghép với Nginx VTS và Loki + Promtail để có bức tranh đầy đủ (cache, lỗi 4xx/5xx, URI bị MISS).

---

## 13. Việc còn lại

- [ ] Xác nhận target job `rgw-usage` là `192.168.69.172:9242` và đang UP (mục 1.5).
- [ ] Chạy `monitor-deploy.sh check` trên lab, đối chiếu với kết quả mong đợi ở mục 4.3.
- [ ] Đổi khóa của `usage-exporter` trước khi dùng ngoài lab (khóa cũ đã xuất hiện trong chat).
- [ ] Đổi mật khẩu Grafana mặc định.
- [ ] Kiểm tra panel tỉ lệ lỗi sau khi nhập dashboard bản mới (mục 7.5).
- [ ] Chọn và cấu hình kênh thông báo (Telegram hoặc email).
- [ ] Cập nhật yêu cầu mới vào task trên Portal (task đang ghi trạng thái HOÀN THÀNH) hoặc tạo task con để nghiệm thu.
- [ ] Triển khai thật: mỗi site một Exporter, nhãn `site`.

---

## Phụ lục A: lệnh nhanh

```bash
# --- Trên S3-GW ---
bash s3gw-prepare.sh --with-test-user
radosgw-admin usage show --uid=test-ops
radosgw-admin user info --uid=usage-exporter | grep -A 25 caps

# --- Trên VM monitor ---
GRAFANA_PASSWORD='***' bash monitor-deploy.sh install --env-file /tmp/rgw-exporter.env --site lab
bash monitor-deploy.sh check
docker logs --tail 30 rgw-usage-exporter
curl -s localhost:9242/metrics | grep radosgw_usage_ops_total | head
docker exec prometheus promtool check config /etc/prometheus/prometheus.yml
curl -X POST http://localhost:9090/-/reload
```

## Phụ lục B: vị trí trong repo

```
docs/guides/s3-rgw-usage-monitoring.md     # bài viết này
tools/s3-rgw-usage/
  s3gw-prepare.sh                          # chạy trên S3-GW
  monitor-deploy.sh                        # chạy trên VM monitor
  rgw-usage-alerts.yml                     # luật cảnh báo Prometheus
  rgw-usage-dashboard.json                 # dashboard Grafana
data/guides.json                           # thông tin bài viết cho mindmap và ô tìm kiếm
```

Cách tải về VM: đặt 4 file trong `tools/s3-rgw-usage/` vào **cùng một thư mục** (ví dụ `/root/s3-rgw-usage/`) rồi chạy theo mục 4.
