# Phase 2 pilot: connect through a read-only backend

This extends the Phase 1 static page with an **opt-in** status collector. The browser never receives the Proxmox API token. The backend only sends fixed HTTPS `GET` requests to the configured PVE origin; it cannot run shell commands or accept arbitrary API paths.

The real cluster is not contacted by the repository build or tests. Do not enter credentials in this repository, source code, chat, browser storage, or a ticket.

## Chỗ nhập thông tin cluster trên VM (không nhập trong Git)

Thông tin kết nối chỉ điền trên VM ứng dụng, trong file `/etc/pve-diagnostic/connector.env`. Không sửa `connector.env.example` thành file thật và không commit file đã điền. Sau khi đã tạo user dịch vụ và thư mục `/etc/pve-diagnostic`, tạo file cấu hình riêng rồi mở bằng `sudoedit`:

```bash
sudo install -o root -g pve-diagnostic -m 640 \
  "$HOME/pve-diagnostic-phase2/prototype/connector.env.example" \
  /etc/pve-diagnostic/connector.env
sudoedit /etc/pve-diagnostic/connector.env
```

Trong editor trên VM, giữ nguyên tên biến và chỉ thay giá trị:

| Biến | Điền giá trị nào |
|---|---|
| `PVE_API_URL` | HTTPS origin của PVE, dạng `https://<hostname-trong-certificate>:8006`; hostname/IP phải khớp TLS certificate. |
| `PVE_API_TOKEN_ID` | Token ID đầy đủ, dạng `<user>@<realm>!<token-name>`; phần user/realm nằm ngay trong ID này. |
| `PVE_API_TOKEN_SECRET` | Secret Proxmox chỉ hiển thị lúc tạo token; nhập trực tiếp vào file trên VM, không gửi qua chat hoặc Git. |
| `PVE_CA_FILE` | Giữ `/etc/pve-diagnostic/pve-root-ca.pem`; cài public CA certificate đã xác minh tại đúng đường dẫn này. |
| `PVE_API_TIMEOUT` | Timeout tính bằng giây; mặc định `8`. |

Không điền password tài khoản người dùng Proxmox. Backend dùng API token riêng; user/token phải được cấp quyền audit-only theo phần bên dưới. Bảo đảm quyền file là `root:pve-diagnostic` và mode `640`. File CA và file cấu hình thật đều nằm ngoài web root và repository.

## Security boundary for the temporary HTTP-over-VPN pilot

The operator has chosen to defer HTTPS for now. Treat that as a short-lived pilot exception, not end-state security:

- Restrict the web app to the VPN/admin source range at both the network firewall and Nginx.
- Keep per-operator Nginx authentication enabled. Use unique credentials, never a shared team password.
- HTTP Basic credentials are not end-to-end encrypted by HTTP. VPN protects traffic only as far as the VPN tunnel endpoint; an internal hop after VPN termination may still be observable.
- The browser sends only a fixed scope (`pve`, `ceph`, `storage`, or `all`) to the same-origin backend. It does not send the incident description.
- The API token is held only in a root-owned environment file on the app VM. The backend binds to `127.0.0.1`; Nginx is the only network-facing proxy.
- The backend verifies the PVE certificate chain and hostname/IP. There is no option to disable TLS verification. If PVE uses a private CA, install only its public CA certificate and verify its fingerprint out-of-band.
- Permit outbound TCP 8006 from the app VM to the named PVE API endpoint only. Do not allow SSH or shell access from the app VM to cluster nodes.
- Do not enable this connector until VPN restriction, Nginx authentication, and the service account/token are independently checked.

The HTTP pilot is appropriate only when the VPN and app VM network path are under the same trusted administrative control. If that cannot be guaranteed, stop and configure HTTPS before enabling credentials or cluster data.

## What the first connector reads

It calls only these fixed endpoints, on operator request:

| Scope | Read-only PVE API resources |
|---|---|
| Proxmox | `/cluster/status`, `/nodes`, `/cluster/resources?type=node`, `/cluster/resources?type=vm` |
| Ceph | `/cluster/ceph/status` |
| Storage | `/cluster/resources?type=storage` |
| All | All of the above |

Response fields are allow-listed before they reach the browser. The connector omits PVE storage configuration details, addresses, Ceph FSID/daemon addresses, credentials, and arbitrary response fields. This first pass displays a timestamped snapshot; it does not claim to identify a root cause or make configuration changes. The operator can compare the snapshot with the local runbooks.

`PVEAuditor` is a convenient read-only starting role but can expose more audit data than these endpoints need. Prefer a custom read-only role with only the required audit privileges after validating the exact API permissions on the installed PVE version. Never grant `Administrator`, `PVEAdmin`, `Sys.Modify`, `VM.PowerMgmt`, or storage/Ceph modification privileges.

## Install backend files on the app VM

The example assumes Debian/Ubuntu, Nginx, and the current web root already contains `/pve-diagnostic/prototype/` and `/pve-diagnostic/docs/`.

1. Copy `server.py` to `/opt/pve-diagnostic/server.py`. Copy `pve-diagnostic.service` to `/etc/systemd/system/pve-diagnostic.service`.
2. Create a dedicated service account and protected config directory:

   ```bash
   sudo useradd --system --no-create-home --shell /usr/sbin/nologin pve-diagnostic
   sudo install -d -o root -g root -m 755 /opt/pve-diagnostic
   sudo install -o root -g root -m 755 server.py /opt/pve-diagnostic/server.py
   sudo install -d -o root -g pve-diagnostic -m 750 /etc/pve-diagnostic
   ```

3. Obtain the PVE public CA certificate from an administrator through a trusted channel. Verify its fingerprint through a separate trusted channel. Install the CA certificate as `/etc/pve-diagnostic/pve-root-ca.pem`, readable by the service account but not writable by it.
4. Create `/etc/pve-diagnostic/connector.env` from `connector.env.example`. Enter the token locally with `sudoedit`; keep it root-owned and readable only by the service group:

   ```bash
   sudo chown root:pve-diagnostic /etc/pve-diagnostic/connector.env
   sudo chmod 640 /etc/pve-diagnostic/connector.env
   ```

   Do this only after creating the restricted API token in PVE. The environment file contains a secret: never copy it back into the repository or share it. `PVE_API_URL` must use a certificate-valid hostname/IP and HTTPS port 8006.

5. Install and start the service:

   ```bash
   sudo install -o root -g root -m 644 pve-diagnostic.service /etc/systemd/system/pve-diagnostic.service
   sudo systemctl daemon-reload
   sudo systemctl enable --now pve-diagnostic
   sudo systemctl status pve-diagnostic --no-pager
   curl --fail http://127.0.0.1:8765/healthz
   ```

   Health status checks only that the local process is serving; it does not contact PVE. Do not expose port 8765 on the VM network.

## Configure Nginx and operator access

1. Create unique Nginx Basic Auth entries for named operators (do not put passwords in shell history):

   ```bash
   sudo apt install apache2-utils
   sudo htpasswd -cB /etc/nginx/pve-diagnostic.htpasswd <operator-name>
   sudo chown root:www-data /etc/nginx/pve-diagnostic.htpasswd
   sudo chmod 640 /etc/nginx/pve-diagnostic.htpasswd
   ```

   For additional operators, use `htpasswd -B` without `-c` so the existing file is preserved. Verify the Nginx worker group on the VM before setting file ownership if it is not `www-data`.

2. Review the existing `server` block, then adapt and include `nginx-location.conf`. Replace `<VPN_CIDR>` with the actual client/source range observed by the VM. Keep the API location protected by the same authentication as the static page.
3. Validate and reload:

   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

4. At the network firewall, allow only the VPN/admin source range to the web VM's current HTTP port. From the web VM, allow only TCP 8006 to the configured PVE API endpoint. Keep port 8765 loopback-only.
5. Confirm without submitting any token that:
   - An unauthenticated browser gets HTTP 401 for `/pve-diagnostic/` and `/pve-diagnostic/api/diagnose`.
   - A VPN client can open `/pve-diagnostic/prototype/` and the directory index is not listed.
   - A non-VPN client is blocked by the firewall/Nginx.
   - `ss -lntp` shows the diagnostic API bound only to `127.0.0.1:8765`.

## Create the PVE read-only identity

Create a dedicated non-human PVE user and an API token with privilege separation enabled. Do not reuse a personal account or `root@pam`.

The initial custom role should contain only read/audit privileges needed by the approved APIs (`Sys.Audit`, `VM.Audit`, and `Datastore.Audit`). With privilege separation enabled, grant the role to both the dedicated user and its token at `/` so effective permissions are their intersection. Validate endpoint permissions with the PVE API Viewer for the cluster's installed version; if a call returns 403, add only the specific audit privilege at the narrowest path required.

Never grant write/action privileges. Store the token secret directly in the app VM's protected environment file; the UI must never ask for it.

## Verify connection without making changes

1. Check the service and logs locally. The logs identify the authenticated operator, HTTP route, and status, but must never contain token headers or response bodies:

   ```bash
   sudo systemctl status pve-diagnostic --no-pager
   sudo journalctl -u pve-diagnostic --since "10 minutes ago" --no-pager
   ```

2. Sign in from a VPN client and select a scope. The browser displays a snapshot only after the operator presses **Thu thập trạng thái live (chỉ đọc)**.
3. Verify that failed TLS validation/401/403 is shown as an explicit error and not replaced by fake/empty success data.
4. Compare each field with the PVE GUI/API Viewer. Do not use the displayed snapshot as an automatic repair decision.
5. Revoke the token immediately if it is exposed; then remove the secret from the app VM and issue a replacement.

## Stop / rollback

Disable the connector without changing the PVE cluster:

```bash
sudo systemctl disable --now pve-diagnostic
```

Then remove the Nginx API proxy location and revoke the dedicated API token in PVE. The static documentation can remain available only if its VPN/auth controls are retained.

Do not proceed to automated diagnosis, command execution, or write-capable access without the operator explicitly approving the next phase.
