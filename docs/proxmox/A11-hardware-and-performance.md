# A11 · Phần cứng và hiệu năng

[← Mục lục](../../README.md) · Proxmox host · 13 lệnh · tên gốc: Hardware and performance

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← A10 Ổ đĩa và filesystem](../proxmox/A10-disks-and-filesystems.md) · [A12 Phân quyền (pveum) →](../proxmox/A12-access-control-pveum.md)

## CPU

```bash
# [chỉ đọc] Thông tin CPU và topology | CPU model and topology
# từ khóa: cpu model core
lscpu

# [chỉ đọc] Bố cục NUMA | NUMA layout
# từ khóa: numa
numactl -H
```

## Bộ nhớ (Memory)

```bash
# [chỉ đọc] Mức dùng RAM | RAM usage
# từ khóa: ram bộ nhớ đầy ram thiếu ram oom out of memory swap
free -h

# [chỉ đọc] Danh sách thanh RAM (DIMM) | DIMM inventory
# từ khóa: ram dimm phần cứng
dmidecode -t memory
```

## Tải hệ thống (Load)

```bash
# [chỉ đọc] Xem tiến trình | Process view
# từ khóa: tiến trình cpu cao treo iowait io wait load average tải ram
top / htop

# [chỉ đọc] Tóm tắt CPU, RAM, IO | CPU, memory, IO summary
# từ khóa: cpu ram io tổng hợp iowait wait wa cao chậm
vmstat 1
```

## Cảm biến (Sensors)

```bash
# [chỉ đọc] Nhiệt độ và quạt | Temperatures and fans
# từ khóa: nhiệt độ quạt nóng
sensors
```

## BMC

```bash
# [chỉ đọc] Đọc cảm biến phần cứng | Sensor readings
# từ khóa: ipmi cảm biến
ipmitool sdr

# [chỉ đọc] Nhật ký sự kiện phần cứng | Hardware event log
# từ khóa: ipmi log lỗi phần cứng sel
ipmitool sel list

# [chỉ đọc] Trạng thái nguồn và khung máy | Power and chassis state
# từ khóa: ipmi nguồn power
ipmitool chassis status

# [chỉ đọc] Cấu hình mạng BMC | BMC network config
# từ khóa: ipmi bmc idrac ip
ipmitool lan print
```

## Log kernel (Kernel log)

```bash
# [chỉ đọc] Thông điệp kernel kèm thời gian | Kernel messages with time
# từ khóa: dmesg lỗi kernel oom io error out of memory i/o đĩa phần cứng
dmesg -T

# [chỉ đọc] Log kernel của lần boot này | Kernel log this boot
# từ khóa: log kernel boot
journalctl -k -b
```

## Case và runbook dùng lệnh trong nhóm này

- [VM không start được](../cases/pve/vm-wont-start.md)
- [Node dừng: HA khởi động lại đồng loạt VM làm tràn RAM (domino)](../cases/pve/ha-domino.md)
- [OSD down hoặc up/down liên tục (flapping)](../cases/ceph/osd-down-flapping.md)
