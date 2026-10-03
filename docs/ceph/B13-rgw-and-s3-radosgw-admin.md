# B13 · RGW and S3 (radosgw-admin)

[← Mục lục](../../README.md) · Ceph · 33 lệnh

[← B12 RBD (VM disks)](../ceph/B12-rbd-vm-disks.md) · [B14 CephFS →](../ceph/B14-cephfs.md)

## Service

```bash
# RGW daemon state
systemctl status ceph-radosgw@rgw.<name>
```

## Users

```bash
# List users
radosgw-admin user list

# User detail and keys
radosgw-admin user info --uid=<uid>

# Create user
radosgw-admin user create --uid=<uid> --display-name=<name>

# Change user
radosgw-admin user modify --uid=<uid> --max-buckets=<n>

# Suspend or enable
radosgw-admin user suspend --uid=<uid> / radosgw-admin user enable --uid=<uid>

# ⚠ NGUY HIỂM: Delete user and data (destructive)
radosgw-admin user rm --uid=<uid> --purge-data
```

## Keys

```bash
# New S3 key
radosgw-admin key create --uid=<uid> --key-type=s3 --gen-access-key --gen-secret

# Remove key
radosgw-admin key rm --uid=<uid> --access-key=<key>
```

## Subuser

```bash
# Create subuser
radosgw-admin subuser create --uid=<uid> --subuser=<uid>:<sub> --access=full
```

## Quota

```bash
# Set user quota
radosgw-admin quota set --quota-scope=user --uid=<uid> --max-size=<bytes> --max-objects=<n>

# Set bucket quota
radosgw-admin quota set --quota-scope=bucket --uid=<uid> --max-size=<bytes>

# Enable quota
radosgw-admin quota enable --quota-scope=user --uid=<uid>
```

## Buckets

```bash
# List buckets
radosgw-admin bucket list

# Buckets of a user
radosgw-admin bucket list --uid=<uid>

# Bucket size, objects, shards
radosgw-admin bucket stats --bucket=<bucket>

# Objects per shard and fill status
radosgw-admin bucket limit check

# Index check
radosgw-admin bucket check --bucket=<bucket>

# ⚠ NGUY HIỂM: Delete bucket (destructive)
radosgw-admin bucket rm --bucket=<bucket> --purge-objects
```

## Reshard

```bash
# Queued reshards
radosgw-admin reshard list

# Reshard state
radosgw-admin reshard status --bucket=<bucket>

# Reshard bucket index
radosgw-admin bucket reshard --bucket=<bucket> --num-shards=<n>
```

## Usage

```bash
# Usage log
radosgw-admin usage show --uid=<uid>
```

## Lifecycle

```bash
# Lifecycle status
radosgw-admin lc list

# Run lifecycle now
radosgw-admin lc process
```

## GC

```bash
# Pending garbage
radosgw-admin gc list --include-all

# Run GC now
radosgw-admin gc process
```

## Topology

```bash
# Zone config
radosgw-admin zone get

# Zonegroup config
radosgw-admin zonegroup get

# Realms
radosgw-admin realm list

# Current period
radosgw-admin period get

# Multisite sync state
radosgw-admin sync status
```

## Index pool

```bash
# Keys in an index object (large omap check)
rados -p <index-pool> listomapkeys <object>
```
