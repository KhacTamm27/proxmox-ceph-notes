# Internal diagnostic prototype

The page is served as static files. When the backend described in [DEPLOYMENT.md](./DEPLOYMENT.md) is installed, the operator may explicitly request a bounded, read-only PVE status snapshot.

## Files

- `template.html`: source for the operator page.
- `index.html`: generated page; do not edit it directly.
- `server.py`: standard-library Python backend. Systemd mode binds to loopback; container mode accepts traffic only through the authenticated host Nginx proxy.
- `pve-diagnostic.service`: systemd service template.
- `nginx-location.conf`: host Nginx Basic Auth reverse proxy template for the single-container app; retain host firewall/VPN restrictions.
- `../Dockerfile`: builds one non-root container containing the static pages/docs and read-only API.
- `../.dockerignore`: keeps local secrets, certificates, and developer files out of Docker build context.
- `connector.env.example`: placeholders only; the populated file belongs on the app VM, never in Git.
- `test_server.py`: local tests using mock API responses. Tests do not contact Proxmox.
- `DEPLOYMENT.md`: security prerequisites, install sequence, read-only token plan and rollback.

## Build

From the repository root, regenerate documentation and the prototype:

```powershell
.\.venv\Scripts\python.exe .\scripts\build.py --repo KhacTamm27/proxmox-ceph-notes
```

The connector backend is not generated into the browser page. The browser sends only an allowed diagnostic scope to the same-origin backend after the operator clicks the collection button. It does not send the issue description or Proxmox token.

## Safety boundary

- Only fixed Proxmox API `GET` routes are implemented; arbitrary paths, shell commands and write methods are not accepted.
- Host checks first verify the requested node against the PVE node list, then query status for that one node only.
- Proxmox API token secrets are read from a protected server-side environment file.
- The backend verifies the PVE TLS certificate and cannot disable certificate verification.
- Responses are projected onto allow-listed fields before being returned to the browser.
- Results and notes are not persisted by the app. Do not enter secrets or unredacted sensitive data.
- The temporary HTTP-over-VPN choice is a risk exception, not end-state guidance. Retain VPN source restrictions and per-operator Nginx authentication; complete HTTPS before broader or long-term use.

Cluster connectivity is opt-in per operator request. Keep the API token and CA on the VM and outside the image/repository.

The container serves `.md` responses as UTF-8 Markdown. Keep the host Nginx as the VPN/auth gateway and publish the container only on `127.0.0.1`; see the single-container section in [DEPLOYMENT.md](./DEPLOYMENT.md).

For a host reboot/hang symptom, search for **Node Proxmox hỏng**, load the node list on demand, select the affected host, and request its host-only status. Uptime provides an approximate current boot time, not a reboot cause or event history. A failed status request is not sufficient evidence that the whole server is frozen; verify out-of-band using console/BMC and the host's logs.
