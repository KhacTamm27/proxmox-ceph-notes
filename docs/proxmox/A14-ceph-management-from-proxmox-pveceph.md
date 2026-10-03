# A14 · Ceph management from Proxmox (pveceph)

[← Mục lục](../../README.md) · Proxmox host · 16 lệnh

[← A13 Tasks, logs and API](../proxmox/A13-tasks-logs-and-api.md)

## Install

```bash
# Install Ceph packages
pveceph install

# Initialize Ceph config
pveceph init --network <cidr> --cluster-network <cidr>
```

## MON

```bash
# Create MON on this node
pveceph mon create

# Remove MON
pveceph mon destroy <id>
```

## MGR

```bash
# Create MGR
pveceph mgr create

# Remove MGR
pveceph mgr destroy <id>
```

## OSD

```bash
# Create OSD
pveceph osd create /dev/<dev>

# ⚠ NGUY HIỂM: Remove OSD (destructive)
pveceph osd destroy <osd-id> --cleanup
```

## Pool

```bash
# List pools
pveceph pool ls

# Create pool and storage
pveceph pool create <pool> --size 3 --min_size 2 --crush_rule <rule> --add_storages 1

# Change pool option
pveceph pool set <pool> --target_size_ratio 0.9

# ⚠ NGUY HIỂM: Delete pool (destructive)
pveceph pool destroy <pool>
```

## CephFS

```bash
# Create MDS
pveceph mds create

# Create CephFS
pveceph fs create --name <fs> --add-storage
```

## Services

```bash
# Start or stop Ceph services on node
pveceph start / pveceph stop
```

## Cleanup

```bash
# ⚠ NGUY HIỂM: Remove Ceph config from node (destructive)
pveceph purge
```
