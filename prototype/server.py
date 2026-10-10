#!/usr/bin/env python3
"""Small, read-only Proxmox API collector for the internal diagnostic prototype."""

from __future__ import annotations

import json
import mimetypes
import os
import re
import ssl
import sys
from datetime import datetime, timedelta, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

MAX_REQUEST_BYTES = 1024
MAX_RESPONSE_BYTES = 1_048_576
ALLOWED_SCOPES = {"all", "pve", "ceph", "storage", "hosts", "host"}
NODE_NAME_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,62}\Z")
CONNECTOR_ENV_KEYS = {
    "PVE_API_URL",
    "PVE_API_TOKEN_ID",
    "PVE_API_TOKEN_SECRET",
    "PVE_CA_FILE",
    "PVE_API_TIMEOUT",
    "PVE_DIAG_BIND",
    "PVE_DIAG_PORT",
}

ENDPOINTS: dict[str, tuple[str, dict[str, str] | None]] = {
    "cluster": ("/cluster/status", None),
    "nodes": ("/nodes", None),
    "node_resources": ("/cluster/resources", {"type": "node"}),
    "vm_resources": ("/cluster/resources", {"type": "vm"}),
    "storage_resources": ("/cluster/resources", {"type": "storage"}),
    "ceph": ("/cluster/ceph/status", None),
}

SCOPE_SOURCES = {
    "all": ("cluster", "nodes", "node_resources", "vm_resources", "storage_resources", "ceph"),
    "pve": ("cluster", "nodes", "node_resources", "vm_resources"),
    "ceph": ("ceph",),
    "storage": ("storage_resources",),
    "hosts": ("nodes",),
}

RESOURCE_FIELDS = {
    "node": (
        "node", "status", "level", "cpu", "maxcpu", "mem", "maxmem",
        "disk", "maxdisk", "uptime",
    ),
    "vm": (
        "vmid", "name", "node", "type", "status", "cpu", "maxcpu",
        "mem", "maxmem", "disk", "maxdisk", "uptime", "ha",
    ),
    "storage": (
        "storage", "node", "type", "status", "total", "used", "avail", "shared",
    ),
}


class ConfigurationError(Exception):
    """Raised when required, safe connector configuration is missing or invalid."""


class ProxmoxApiError(Exception):
    """A sanitized error suitable for returning to the operator."""


def load_env_file(path: str) -> None:
    try:
        lines = open(path, encoding="utf-8")
    except OSError as exc:
        raise ConfigurationError("Could not read the mounted connector environment file.") from exc
    with lines:
        for line_number, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            key, separator, value = line.partition("=")
            if (
                not separator
                or not re.fullmatch(r"[A-Z][A-Z0-9_]*", key)
                or key not in CONNECTOR_ENV_KEYS
                or not value.strip()
            ):
                raise ConfigurationError(
                    f"Invalid connector environment setting on line {line_number}."
                )
            os.environ.setdefault(key, value.strip())


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ConfigurationError(f"Required setting {name} is not configured.")
    return value


def api_url_from_env() -> str:
    raw_url = _required_env("PVE_API_URL")
    parsed = urlsplit(raw_url)
    try:
        port = parsed.port
    except ValueError as exc:
        raise ConfigurationError("PVE_API_URL contains an invalid port.") from exc
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or port is None
        or not 1 <= port <= 65535
        or parsed.username
        or parsed.password
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        raise ConfigurationError(
            "PVE_API_URL must be an HTTPS origin such as https://pve.example:8006."
        )
    return raw_url.rstrip("/")


def tls_context_from_env() -> ssl.SSLContext:
    ca_file = os.environ.get("PVE_CA_FILE", "").strip() or None
    try:
        return ssl.create_default_context(cafile=ca_file)
    except (OSError, ssl.SSLError) as exc:
        raise ConfigurationError("Could not load the configured Proxmox CA file.") from exc


def unwrap_api_data(payload: Any) -> Any:
    if isinstance(payload, dict) and "data" in payload:
        return payload["data"]
    return payload


def project_resource(payload: Any, resource_type: str) -> list[dict[str, Any]]:
    data = unwrap_api_data(payload)
    if not isinstance(data, list):
        raise ProxmoxApiError("Proxmox returned an unexpected resource list.")
    allowed_fields = RESOURCE_FIELDS[resource_type]
    return [
        {key: row[key] for key in allowed_fields if key in row}
        for row in data
        if isinstance(row, dict)
    ]


def project_cluster(payload: Any) -> list[dict[str, Any]]:
    data = unwrap_api_data(payload)
    if not isinstance(data, list):
        raise ProxmoxApiError("Proxmox returned an unexpected cluster status.")
    allowed = (
        "id", "name", "type", "local", "online", "nodeid",
        "quorate", "votes", "expected_votes", "total_votes",
    )
    return [
        {key: row[key] for key in allowed if key in row}
        for row in data
        if isinstance(row, dict)
    ]


def project_node_status(payload: Any) -> dict[str, Any]:
    data = unwrap_api_data(payload)
    if not isinstance(data, dict):
        raise ProxmoxApiError("Proxmox returned an unexpected node status.")

    result: dict[str, Any] = {}
    for field in ("uptime", "cpu", "wait", "pveversion", "kversion"):
        value = data.get(field)
        if isinstance(value, (str, int, float)):
            result[field] = value
    for field in ("loadavg",):
        value = data.get(field)
        if isinstance(value, list) and all(
            isinstance(item, (str, int, float)) for item in value
        ):
            result[field] = value
    for section in ("memory", "swap", "rootfs"):
        value = data.get(section)
        if isinstance(value, dict):
            result[section] = {
                key: value[key]
                for key in ("total", "used", "free", "avail")
                if key in value and isinstance(value[key], (int, float))
            }
    return result


def project_ceph(payload: Any) -> dict[str, Any]:
    data = unwrap_api_data(payload)
    if not isinstance(data, dict):
        raise ProxmoxApiError("Proxmox returned an unexpected Ceph status.")

    result: dict[str, Any] = {}
    health = data.get("health")
    if isinstance(health, dict):
        projected_health: dict[str, Any] = {}
        if isinstance(health.get("status"), str):
            projected_health["status"] = health["status"]
        checks = health.get("checks")
        if isinstance(checks, dict):
            projected_checks: dict[str, Any] = {}
            for check_id, check in checks.items():
                if not isinstance(check_id, str) or not isinstance(check, dict):
                    continue
                projected: dict[str, Any] = {}
                for field in ("severity", "summary"):
                    value = check.get(field)
                    if isinstance(value, (str, int, float)):
                        projected[field] = value
                summaries = check.get("summary")
                if isinstance(summaries, list):
                    projected["summary"] = [
                        item.get("message", "")
                        for item in summaries
                        if isinstance(item, dict) and isinstance(item.get("message"), str)
                    ]
                projected_checks[check_id] = projected
            projected_health["checks"] = projected_checks
        result["health"] = projected_health

    for section, fields in (
        ("monmap", ("num_mons",)),
        ("osdmap", ("num_osds", "num_up_osds", "num_in_osds")),
        ("pgmap", (
            "num_pgs", "num_objects", "bytes_used", "bytes_total", "bytes_avail",
            "read_bytes_sec", "write_bytes_sec", "read_op_per_sec", "write_op_per_sec",
            "pgs_by_state",
        )),
    ):
        value = data.get(section)
        if isinstance(value, dict):
            nested = value.get(section)
            if isinstance(nested, dict):
                value = nested
            projected_section = {
                key: value[key]
                for key in fields
                if key in value and isinstance(value[key], (str, int, float, list, dict))
            }
            if projected_section:
                result[section] = projected_section
    return result


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(
        self,
        _request: Request,
        _response: Any,
        _code: int,
        _message: str,
        _headers: Any,
        _new_url: str,
    ) -> None:
        return None


class ProxmoxClient:
    def __init__(
        self,
        api_url: str,
        token_id: str,
        token_secret: str,
        tls_context: ssl.SSLContext,
        timeout: float = 8.0,
    ) -> None:
        self.api_url = api_url.rstrip("/")
        self.authorization = f"PVEAPIToken={token_id}={token_secret}"
        self.tls_context = tls_context
        self.timeout = timeout
        self.opener = build_opener(
            HTTPSHandler(context=tls_context),
            NoRedirectHandler(),
        )

    def get(self, source: str) -> Any:
        if source not in ENDPOINTS:
            raise ProxmoxApiError("Requested Proxmox API endpoint is not allowed.")
        path, query = ENDPOINTS[source]
        query_string = f"?{urlencode(query)}" if query else ""
        return self._get_path(f"{path}{query_string}")

    def get_node_status(self, node: str) -> Any:
        if not NODE_NAME_PATTERN.fullmatch(node):
            raise ProxmoxApiError("The selected Proxmox node name is invalid.")
        return self._get_path(f"/nodes/{quote(node, safe='')}/status")

    def _get_path(self, path: str) -> Any:
        request = Request(
            f"{self.api_url}/api2/json{path}",
            headers={
                "Accept": "application/json",
                "Authorization": self.authorization,
            },
            method="GET",
        )
        try:
            with self.opener.open(
                request,
                timeout=self.timeout,
            ) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
        except HTTPError as exc:
            if exc.code in (401, 403):
                raise ProxmoxApiError(
                    f"Proxmox denied the read request (HTTP {exc.code}); verify token permissions."
                ) from exc
            raise ProxmoxApiError(
                f"Proxmox API request failed (HTTP {exc.code})."
            ) from exc
        except (URLError, TimeoutError, ssl.SSLError, OSError) as exc:
            raise ProxmoxApiError(
                "Could not reach Proxmox over verified HTTPS; check routing, timeout, and CA trust."
            ) from exc

        if len(raw) > MAX_RESPONSE_BYTES:
            raise ProxmoxApiError("Proxmox response exceeded the configured size limit.")
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProxmoxApiError("Proxmox returned invalid JSON.") from exc


def _read_only_client() -> ProxmoxClient:
    token_id = _required_env("PVE_API_TOKEN_ID")
    token_secret = _required_env("PVE_API_TOKEN_SECRET")
    if not re.fullmatch(r"[^=\s]+", token_id) or any(
        char.isspace() or ord(char) < 32 or ord(char) == 127 for char in token_secret
    ):
        raise ConfigurationError("The configured API token ID or secret has invalid characters.")
    timeout_text = os.environ.get("PVE_API_TIMEOUT", "8")
    try:
        timeout = float(timeout_text)
    except ValueError as exc:
        raise ConfigurationError("PVE_API_TIMEOUT must be a number from 1 to 30.") from exc
    if not 1 <= timeout <= 30:
        raise ConfigurationError("PVE_API_TIMEOUT must be a number from 1 to 30.")
    return ProxmoxClient(
        api_url_from_env(),
        token_id,
        token_secret,
        tls_context_from_env(),
        timeout,
    )


def _project(source: str, payload: Any) -> Any:
    if source == "cluster":
        return project_cluster(payload)
    if source == "nodes":
        return project_resource(payload, "node")
    if source == "node_resources":
        return project_resource(payload, "node")
    if source == "vm_resources":
        return project_resource(payload, "vm")
    if source == "storage_resources":
        return project_resource(payload, "storage")
    if source == "ceph":
        return project_ceph(payload)
    raise ProxmoxApiError("Unknown response projection.")


def collect_snapshot(scope: str, client: ProxmoxClient | None = None) -> dict[str, Any]:
    if scope not in SCOPE_SOURCES:
        raise ValueError("Unsupported diagnostic scope.")
    api_client = client or _read_only_client()
    snapshot: dict[str, Any] = {
        "scope": scope,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "sources": {},
        "errors": [],
    }
    for source in SCOPE_SOURCES[scope]:
        try:
            snapshot["sources"][source] = _project(source, api_client.get(source))
        except ProxmoxApiError as exc:
            snapshot["errors"].append({"source": source, "message": str(exc)})
    if not snapshot["sources"]:
        raise ProxmoxApiError(
            snapshot["errors"][0]["message"] if snapshot["errors"] else "No status data was collected."
        )
    return snapshot


def collect_host_snapshot(
    node: str,
    client: ProxmoxClient | None = None,
) -> dict[str, Any]:
    if not isinstance(node, str) or not NODE_NAME_PATTERN.fullmatch(node):
        raise ValueError("Invalid Proxmox node name.")
    api_client = client or _read_only_client()
    node_rows = project_resource(api_client.get("nodes"), "node")
    selected = next((row for row in node_rows if row.get("node") == node), None)
    if selected is None:
        raise ValueError("Selected host was not found in the Proxmox node list.")

    collected_at = datetime.now(timezone.utc)
    snapshot: dict[str, Any] = {
        "scope": "host",
        "node": node,
        "collected_at": collected_at.isoformat(),
        "sources": {
            "membership": {
                key: selected[key]
                for key in ("node", "status", "uptime")
                if key in selected
            }
        },
        "errors": [],
    }
    try:
        status = project_node_status(api_client.get_node_status(node))
        if isinstance(status.get("uptime"), (int, float)) and status["uptime"] >= 0:
            status["estimated_boot_at"] = (
                collected_at - timedelta(seconds=status["uptime"])
            ).isoformat()
        snapshot["sources"]["node_status"] = status
    except ProxmoxApiError as exc:
        snapshot["errors"].append({"source": "node_status", "message": str(exc)})
    return snapshot


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class DiagnosticHandler(SimpleHTTPRequestHandler):
    server_version = "PveDiagnostic"
    sys_version = ""
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".md": "text/markdown; charset=utf-8",
        ".json": "application/json; charset=utf-8",
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        web_root = os.environ.get("PVE_DIAG_WEB_ROOT", "").strip() or None
        super().__init__(*args, directory=web_root, **kwargs)

    def translate_path(self, path: str) -> str:
        clean_path = unquote(urlsplit(path).path)
        if clean_path == "/":
            clean_path = "/index.html"
        elif clean_path.startswith("/pve-diagnostic/"):
            clean_path = clean_path[len("/pve-diagnostic"):]
        return super().translate_path(clean_path)

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def list_directory(self, path: str) -> None:
        self.send_error(404, "Directory listing is disabled.")
        return None

    def do_GET(self) -> None:
        if self.path != "/healthz":
            if not self.headers.get("X-Authenticated-User", "").strip():
                _json_response(self, 401, {"error": "Operator authentication is required."})
                return
            super().do_GET()
            return
        configured = all(
            os.environ.get(name, "").strip()
            for name in ("PVE_API_URL", "PVE_API_TOKEN_ID", "PVE_API_TOKEN_SECRET")
        )
        _json_response(self, 200, {"status": "ok", "collector_configured": configured})

    def do_POST(self) -> None:
        if self.path not in ("/api/diagnose", "/pve-diagnostic/api/diagnose"):
            _json_response(self, 404, {"error": "Not found."})
            return
        if not self.headers.get("X-Authenticated-User", "").strip():
            _json_response(self, 401, {"error": "Operator authentication is required."})
            return
        if self.headers.get_content_type() != "application/json":
            _json_response(self, 415, {"error": "Content-Type must be application/json."})
            return
        origin = self.headers.get("Origin")
        if origin:
            host = self.headers.get("Host", "")
            if origin not in (f"http://{host}", f"https://{host}"):
                _json_response(self, 403, {"error": "Cross-origin requests are not accepted."})
                return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            _json_response(self, 400, {"error": "Invalid request length."})
            return
        if content_length < 1 or content_length > MAX_REQUEST_BYTES:
            _json_response(self, 413, {"error": "Request body is empty or exceeds the size limit."})
            return
        try:
            body = json.loads(self.rfile.read(content_length))
        except (UnicodeDecodeError, json.JSONDecodeError):
            _json_response(self, 400, {"error": "Request body must be valid JSON."})
            return
        if not isinstance(body, dict) or "scope" not in body:
            _json_response(self, 400, {"error": "Request must contain a diagnostic scope."})
            return
        scope = body["scope"]
        if not isinstance(scope, str) or scope not in ALLOWED_SCOPES:
            _json_response(self, 400, {"error": "Unsupported diagnostic scope."})
            return
        if scope == "host":
            if set(body) != {"scope", "node"}:
                _json_response(self, 400, {"error": "Host checks require only scope and node."})
                return
            if not isinstance(body["node"], str) or not NODE_NAME_PATTERN.fullmatch(body["node"]):
                _json_response(self, 400, {"error": "Invalid Proxmox node name."})
                return
        elif set(body) != {"scope"}:
            _json_response(self, 400, {"error": "Request must contain only the diagnostic scope."})
            return
        try:
            if scope == "host":
                result = collect_host_snapshot(body["node"])
            else:
                result = collect_snapshot(scope)
        except ConfigurationError as exc:
            _json_response(self, 503, {"error": str(exc)})
            return
        except ValueError as exc:
            _json_response(self, 400, {"error": str(exc)})
            return
        except ProxmoxApiError as exc:
            _json_response(self, 502, {"error": str(exc)})
            return
        _json_response(self, 200, result)

    def log_message(self, format_string: str, *args: Any) -> None:
        operator = self.headers.get("X-Authenticated-User", "unauthenticated")
        message = format_string % args
        print(
            json.dumps(
                {
                    "time": datetime.now(timezone.utc).isoformat(),
                    "operator": operator,
                    "request": message,
                },
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )


def main() -> None:
    env_file = os.environ.get("PVE_DIAG_ENV_FILE", "").strip()
    if env_file:
        try:
            load_env_file(env_file)
        except ConfigurationError as exc:
            raise SystemExit(str(exc)) from exc
    host = os.environ.get("PVE_DIAG_BIND", "127.0.0.1")
    port_text = os.environ.get("PVE_DIAG_PORT", "8765")
    try:
        port = int(port_text)
    except ValueError as exc:
        raise SystemExit("PVE_DIAG_PORT must be an integer.") from exc
    trusted_proxy = os.environ.get("PVE_DIAG_TRUSTED_PROXY") == "1"
    if (
        not 1 <= port <= 65535
        or (host != "127.0.0.1" and not trusted_proxy)
        or (trusted_proxy and host not in ("0.0.0.0", "::"))
    ):
        raise SystemExit(
            "Non-loopback binding requires trusted-proxy mode and proxy-provided authentication."
        )
    server = ThreadingHTTPServer((host, port), DiagnosticHandler)
    server.daemon_threads = True
    print(f"Read-only diagnostic API listening on {host}:{port}", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
