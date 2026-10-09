# A11 · Hardware and performance

[← Mục lục](../../README.md) · Proxmox host · 13 lệnh

[← A10 Disks and filesystems](../proxmox/A10-disks-and-filesystems.md) · [A12 Access control (pveum) →](../proxmox/A12-access-control-pveum.md)

## CPU

```bash
# Thông tin CPU và topology | CPU model and topology
# từ khóa: cpu model core
lscpu

# Bố cục NUMA | NUMA layout
# từ khóa: numa
numactl -H
```

## Memory

```bash
# Mức dùng RAM | RAM usage
# từ khóa: ram bộ nhớ đầy ram thiếu ram
free -h

# Danh sách thanh RAM (DIMM) | DIMM inventory
# từ khóa: ram dimm phần cứng
dmidecode -t memory
```

## Load

```bash
# Xem tiến trình | Process view
# từ khóa: tiến trình cpu cao treo
top / htop

# Tóm tắt CPU, RAM, IO | CPU, memory, IO summary
# từ khóa: cpu ram io tổng hợp
vmstat 1
```

## Sensors

```bash
# Nhiệt độ và quạt | Temperatures and fans
# từ khóa: nhiệt độ quạt nóng
sensors
```

## BMC

```bash
# Đọc cảm biến phần cứng | Sensor readings
# từ khóa: ipmi cảm biến
ipmitool sdr

# Nhật ký sự kiện phần cứng | Hardware event log
# từ khóa: ipmi log lỗi phần cứng sel
ipmitool sel list

# Trạng thái nguồn và khung máy | Power and chassis state
# từ khóa: ipmi nguồn power
ipmitool chassis status

# Cấu hình mạng BMC | BMC network config
# từ khóa: ipmi bmc idrac ip
ipmitool lan print
```

## Kernel log

```bash
# Thông điệp kernel kèm thời gian | Kernel messages with time
# từ khóa: dmesg lỗi kernel oom io error
dmesg -T

# Log kernel của lần boot này | Kernel log this boot
# từ khóa: log kernel boot
journalctl -k -b
```
