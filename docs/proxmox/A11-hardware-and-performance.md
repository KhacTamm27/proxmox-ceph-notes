# A11 · Hardware and performance

[← Mục lục](../../README.md) · Proxmox host · 13 lệnh

[← A10 Disks and filesystems](../proxmox/A10-disks-and-filesystems.md) · [A12 Access control (pveum) →](../proxmox/A12-access-control-pveum.md)

## CPU

```bash
# CPU model and topology
lscpu

# NUMA layout
numactl -H
```

## Memory

```bash
# RAM usage
free -h

# DIMM inventory
dmidecode -t memory
```

## Load

```bash
# Process view
top / htop

# CPU, memory, IO summary
vmstat 1
```

## Sensors

```bash
# Temperatures and fans
sensors
```

## BMC

```bash
# Sensor readings
ipmitool sdr

# Hardware event log
ipmitool sel list

# Power and chassis state
ipmitool chassis status

# BMC network config
ipmitool lan print
```

## Kernel log

```bash
# Kernel messages with time
dmesg -T

# Kernel log this boot
journalctl -k -b
```
