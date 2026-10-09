# A12 · Access control (pveum)

[← Mục lục](../../README.md) · Proxmox host · 8 lệnh

[← A11 Hardware and performance](../proxmox/A11-hardware-and-performance.md) · [A13 Tasks, logs and API →](../proxmox/A13-tasks-logs-and-api.md)

## Users

```bash
# Liệt kê user | List users
# từ khóa: user người dùng
pveum user list

# Tạo user | Create user
# từ khóa: tạo user
pveum user add <user>@pve --password <p>

# Đổi mật khẩu user | Change password
# từ khóa: đổi mật khẩu password
pveum passwd <user>@pve
```

## Roles

```bash
# Liệt kê role | List roles
# từ khóa: role vai trò
pveum role list
```

## Permissions

```bash
# Liệt kê ACL (phân quyền) | List ACLs
# từ khóa: acl phân quyền permission
pveum acl list

# Cấp quyền cho user trên VM | Grant permission
# từ khóa: cấp quyền phân quyền vm user
pveum acl modify /vms/<vmid> --users <user>@pve --roles PVEVMAdmin
```

## Tokens

```bash
# Tạo API token | API token
# từ khóa: api token
pveum user token add <user>@pve <token-id> --privsep 1
```

## Realms

```bash
# Liệt kê realm xác thực | Auth realms
# từ khóa: realm sso ldap xác thực
pveum realm list
```
