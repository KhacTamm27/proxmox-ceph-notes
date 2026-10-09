# Internal diagnostic prototype

The page is served as static files. When the backend described in [DEPLOYMENT.md](./DEPLOYMENT.md) is installed, the operator may explicitly request a bounded, read-only PVE status snapshot.

## Files

- `template.html`: source for the operator page.
- `index.html`: generated page; do not edit it directly.
- `server.py`: standard-library Python backend. The service binds to loopback only.
- `pve-diagnostic.service`: systemd service template.
- `nginx-location.conf`: VPN allow-list, Nginx authentication, static path and same-origin API proxy template.
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
- Proxmox API token secrets are read from a protected server-side environment file.
- The backend verifies the PVE TLS certificate and cannot disable certificate verification.
- Responses are projected onto allow-listed fields before being returned to the browser.
- Results and notes are not persisted by the app. Do not enter secrets or unredacted sensitive data.
- The temporary HTTP-over-VPN choice is a risk exception, not end-state guidance. Retain VPN source restrictions and per-operator Nginx authentication; complete HTTPS before broader or long-term use.

Cluster connectivity remains off until the backend service and protected token configuration are explicitly installed on the VM.
