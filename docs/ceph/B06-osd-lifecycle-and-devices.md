# B6 · OSD lifecycle and devices

[← Mục lục](../../README.md) · Ceph · 15 lệnh

[← B5 OSD flags and maintenance](../ceph/B05-osd-flags-and-maintenance.md) · [B7 OSD daemon and performance (admin socket) →](../ceph/B07-osd-daemon-and-performance-admin-socket.md)

## Inventory

```bash
# Devices usable for OSDs (on OSD host)
ceph-volume inventory

# OSD to device mapping (on OSD host)
ceph-volume lvm list
```

## Create

```bash
# Create OSD (on OSD host)
ceph-volume lvm create --data /dev/<dev>

# Activate OSDs after reboot
ceph-volume lvm activate --all
```

## Replace

```bash
# ⚠ NGUY HIỂM: Destroy OSD, keep ID (destructive)
ceph osd destroy <osd-id> --yes-i-really-mean-it
```

## Remove

```bash
# ⚠ NGUY HIỂM: Remove OSD from cluster (destructive)
ceph osd purge <osd-id> --yes-i-really-mean-it
```

## Wipe

```bash
# ⚠ NGUY HIỂM: Wipe device (destructive)
ceph-volume lvm zap /dev/<dev> --destroy
```

## Service

```bash
# OSD daemon state
systemctl status ceph-osd@<osd-id>

# Restart OSD
systemctl restart ceph-osd@<osd-id>

# OSD log
journalctl -u ceph-osd@<osd-id> -f
```

## BlueStore

```bash
# Read OSD label
ceph-bluestore-tool show-label --dev /dev/<dev>

# Check store (OSD stopped)
ceph-bluestore-tool fsck --path /var/lib/ceph/osd/ceph-<id>
```

## Maintenance

```bash
# Compact RocksDB
ceph tell osd.<id> compact
```

## Class

```bash
# Set device class
ceph osd crush set-device-class nvme osd.<id>

# Remove device class
ceph osd crush rm-device-class osd.<id>
```
