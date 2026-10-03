# B8 · CRUSH map

[← Mục lục](../../README.md) · Ceph · 19 lệnh

[← B7 OSD daemon and performance (admin socket)](../ceph/B07-osd-daemon-and-performance-admin-socket.md) · [B9 Pools →](../ceph/B09-pools.md)

## View

```bash
# CRUSH hierarchy
ceph osd crush tree

# Device classes
ceph osd crush class ls

# Tunables profile
ceph osd crush tunables show
```

## Rules

```bash
# List rules
ceph osd crush rule ls

# Rule detail
ceph osd crush rule dump <rule>

# Create replicated rule
ceph osd crush rule create-replicated <rule> <root> <type> [<class>]

# Create EC rule
ceph osd crush rule create-erasure <rule> <profile>

# ⚠ NGUY HIỂM: Delete rule (destructive)
ceph osd crush rule rm <rule>
```

## Buckets

```bash
# Create bucket
ceph osd crush add-bucket <name> <type>

# Move bucket
ceph osd crush move <name> <type>=<parent>

# Add extra parent
ceph osd crush link <name> <type>=<parent>

# Rename bucket
ceph osd crush rename-bucket <old> <new>

# ⚠ NGUY HIỂM: Remove bucket or item (destructive)
ceph osd crush remove <name>
```

## Map file

```bash
# Export compiled map
ceph osd getcrushmap -o crush.bin

# Decompile
crushtool -d crush.bin -o crush.txt

# Compile
crushtool -c crush.txt -o crush.new

# Validate mappings
crushtool -i crush.bin --test --rule <n> --num-rep 3 --show-bad-mappings

# Simulate distribution
crushtool -i crush.bin --test --rule <n> --num-rep 3 --show-utilization

# Apply map (can trigger rebalance)
ceph osd setcrushmap -i crush.new
```
