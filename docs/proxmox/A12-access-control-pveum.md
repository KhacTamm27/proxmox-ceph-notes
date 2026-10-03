# A12 · Access control (pveum)

[← Mục lục](../../README.md) · Proxmox host · 8 lệnh

[← A11 Hardware and performance](../proxmox/A11-hardware-and-performance.md) · [A13 Tasks, logs and API →](../proxmox/A13-tasks-logs-and-api.md)

## Users

```bash
# List users
pveum user list

# Create user
pveum user add <user>@pve --password <p>

# Change password
pveum passwd <user>@pve
```

## Roles

```bash
# List roles
pveum role list
```

## Permissions

```bash
# List ACLs
pveum acl list

# Grant permission
pveum acl modify /vms/<vmid> --users <user>@pve --roles PVEVMAdmin
```

## Tokens

```bash
# API token
pveum user token add <user>@pve <token-id> --privsep 1
```

## Realms

```bash
# Auth realms
pveum realm list
```
