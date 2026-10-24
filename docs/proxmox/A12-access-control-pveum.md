# A12 · Phân quyền (pveum)

[← Mục lục](../../README.md) · Proxmox host · 8 lệnh · tên gốc: Access control (pveum)

Ký hiệu: `[chỉ đọc]` chỉ xem trạng thái, không thay đổi hệ thống; `⚠ NGUY HIỂM` phá hủy hoặc ảnh hưởng dịch vụ; không ghi chú gì là lệnh có thay đổi cấu hình hoặc trạng thái, đọc kỹ trước khi chạy.

[← A11 Phần cứng và hiệu năng](../proxmox/A11-hardware-and-performance.md) · [A13 Task, log và API →](../proxmox/A13-tasks-logs-and-api.md)

## User (Users)

```bash
# [chỉ đọc] Liệt kê user | List users
# từ khóa: user người dùng
pveum user list

# Tạo user | Create user
# từ khóa: tạo user
pveum user add <user>@pve --password <p>

# Đổi mật khẩu user | Change password
# từ khóa: đổi mật khẩu password root reset quên
pveum passwd <user>@pve
```

## Vai trò (Roles)

```bash
# [chỉ đọc] Liệt kê role | List roles
# từ khóa: role vai trò
pveum role list
```

## Phân quyền (Permissions)

```bash
# [chỉ đọc] Liệt kê ACL (phân quyền) | List ACLs
# từ khóa: acl phân quyền permission
pveum acl list

# Cấp quyền cho user trên VM | Grant permission
# từ khóa: cấp quyền phân quyền vm user
pveum acl modify /vms/<vmid> --users <user>@pve --roles PVEVMAdmin
```

## Token (Tokens)

```bash
# Tạo API token | API token
# từ khóa: api token
pveum user token add <user>@pve <token-id> --privsep 1
```

## Realm xác thực (Realms)

```bash
# [chỉ đọc] Liệt kê realm xác thực | Auth realms
# từ khóa: realm sso ldap xác thực
pveum realm list
```

## Case và runbook dùng lệnh trong nhóm này

- [Cấu hình Nginx proxy console cho VM Proxmox (noVNC qua portal)](../runbooks/rb-console-proxy-nginx.md)
- [Console VM qua proxy không kết nối (màn hình đen, 401, 403, 404, 502, WebSocket đứt)](../cases/pve/console-proxy-fail.md)
