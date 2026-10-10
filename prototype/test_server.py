import json
import http.client
import os
import ssl
import tempfile
import threading
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from prototype import server


class FakeClient:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def get(self, source):
        self.calls.append(source)
        response = self.responses[source]
        if isinstance(response, Exception):
            raise response
        return response

    def get_node_status(self, node):
        self.calls.append(f"node_status:{node}")
        response = self.responses[f"node_status:{node}"]
        if isinstance(response, Exception):
            raise response
        return response


class Response(BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        self.close()


class ProxmoxClientTests(unittest.TestCase):
    def setUp(self):
        with patch("prototype.server.build_opener") as build_opener:
            self.client = server.ProxmoxClient(
                "https://pve.example:8006",
                "diagnostic@pve!reader",
                "test-secret",
                ssl.create_default_context(),
            )
        self.opener = build_opener.return_value

    def test_requests_only_allowlisted_get_url_with_token_header(self):
        self.opener.open.return_value = Response(b'{"data": []}')
        result = self.client.get("vm_resources")
        request = self.opener.open.call_args.args[0]
        self.assertEqual(result, {"data": []})
        self.assertEqual(request.method, "GET")
        self.assertEqual(
            request.full_url,
            "https://pve.example:8006/api2/json/cluster/resources?type=vm",
        )
        self.assertEqual(
            request.get_header("Authorization"),
            "PVEAPIToken=diagnostic@pve!reader=test-secret",
        )

    def test_requests_only_the_selected_node_status_endpoint(self):
        self.opener.open.return_value = Response(b'{"data": {"uptime": 3600}}')
        result = self.client.get_node_status("pve1")
        request = self.opener.open.call_args.args[0]
        self.assertEqual(result, {"data": {"uptime": 3600}})
        self.assertEqual(
            request.full_url,
            "https://pve.example:8006/api2/json/nodes/pve1/status",
        )
        self.assertEqual(request.method, "GET")

    def test_rejects_path_like_node_names(self):
        for node in ("../cluster/status", "pve1/status", ""):
            with self.subTest(node=node):
                with self.assertRaises(server.ProxmoxApiError):
                    self.client.get_node_status(node)

    def test_rejects_unknown_endpoint(self):
        with self.assertRaises(server.ProxmoxApiError):
            self.client.get("/nodes/other/status")

    def test_rejects_plain_http_api_url(self):
        with patch.dict(os.environ, {"PVE_API_URL": "http://pve.example:8006"}):
            with self.assertRaises(server.ConfigurationError):
                server.api_url_from_env()

    def test_env_file_loader_accepts_only_known_connector_settings(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / "connector.env"
            env_file.write_text(
                "PVE_API_URL=https://pve.example:8006\n"
                "PVE_API_TOKEN_SECRET=secret=with=equals\n",
                encoding="utf-8",
            )
            with patch.dict(os.environ, {}, clear=True):
                server.load_env_file(str(env_file))
                self.assertEqual(os.environ["PVE_API_URL"], "https://pve.example:8006")
                self.assertEqual(
                    os.environ["PVE_API_TOKEN_SECRET"],
                    "secret=with=equals",
                )

            env_file.write_text("PYTHONPATH=/tmp/attacker\n", encoding="utf-8")
            with self.assertRaises(server.ConfigurationError):
                server.load_env_file(str(env_file))


class ProjectionTests(unittest.TestCase):
    def test_resource_projection_excludes_unapproved_fields(self):
        result = server.project_resource(
            {
                "data": [
                    {
                        "vmid": 101,
                        "name": "app-vm",
                        "node": "pve1",
                        "status": "running",
                        "cpu": 0.25,
                        "mem": 10,
                        "secret": "must-not-leak",
                    }
                ]
            },
            "vm",
        )
        self.assertEqual(len(result), 1)
        self.assertNotIn("secret", result[0])
        self.assertEqual(result[0]["vmid"], 101)

    def test_ceph_projection_excludes_fsid_and_daemon_addresses(self):
        result = server.project_ceph(
            {
                "data": {
                    "fsid": "private-cluster-id",
                    "health": {"status": "HEALTH_WARN", "checks": {}},
                    "monmap": {"num_mons": 3, "mons": [{"addr": "10.0.0.1"}]},
                    "osdmap": {"osdmap": {"num_osds": 4, "num_up_osds": 3, "secret": "omit"}},
                    "pgmap": {"pgmap": {"num_pgs": 64}},
                }
            }
        )
        self.assertEqual(result["health"]["status"], "HEALTH_WARN")
        self.assertEqual(result["monmap"], {"num_mons": 3})
        self.assertNotIn("fsid", result)
        self.assertNotIn("mons", result["monmap"])
        self.assertNotIn("secret", result["osdmap"])

    def test_node_status_projection_keeps_only_diagnostic_fields(self):
        result = server.project_node_status(
            {
                "data": {
                    "uptime": 7200,
                    "cpu": 0.2,
                    "wait": 0.01,
                    "loadavg": ["0.10", "0.20", "0.30"],
                    "memory": {"total": 1000, "used": 400, "free": 600, "secret": "omit"},
                    "rootfs": {"total": 2000, "used": 500, "avail": 1500},
                    "network": {"interfaces": ["private-interface"]},
                    "secret": "must-not-leak",
                }
            }
        )
        self.assertEqual(result["uptime"], 7200)
        self.assertEqual(result["memory"], {"total": 1000, "used": 400, "free": 600})
        self.assertNotIn("network", result)
        self.assertNotIn("secret", result)
        self.assertNotIn("secret", result["memory"])


class CollectionTests(unittest.TestCase):
    def test_ceph_scope_reads_only_ceph_status(self):
        client = FakeClient({"ceph": {"data": {"health": {"status": "HEALTH_OK"}}}})
        result = server.collect_snapshot("ceph", client)
        self.assertEqual(client.calls, ["ceph"])
        self.assertEqual(result["sources"]["ceph"]["health"]["status"], "HEALTH_OK")
        self.assertIn("collected_at", result)

    def test_hosts_scope_reads_only_the_node_list(self):
        client = FakeClient({"nodes": {"data": [{"node": "pve1", "status": "online"}]}})
        result = server.collect_snapshot("hosts", client)
        self.assertEqual(client.calls, ["nodes"])
        self.assertEqual(result["sources"]["nodes"], [{"node": "pve1", "status": "online"}])

    def test_pve_scope_uses_fixed_sources_and_keeps_partial_errors(self):
        responses = {
            "cluster": {"data": [{"type": "cluster", "quorate": 1}]},
            "nodes": {"data": [{"node": "pve1", "status": "online"}]},
            "node_resources": {"data": [{"node": "pve1", "status": "online"}]},
            "vm_resources": server.ProxmoxApiError("Proxmox denied the read request (HTTP 403); verify token permissions."),
        }
        client = FakeClient(responses)
        result = server.collect_snapshot("pve", client)
        self.assertEqual(client.calls, ["cluster", "nodes", "node_resources", "vm_resources"])
        self.assertIn("cluster", result["sources"])
        self.assertEqual(result["errors"][0]["source"], "vm_resources")

    def test_rejects_unknown_scope(self):
        with self.assertRaises(ValueError):
            server.collect_snapshot("custom", FakeClient({}))
        with self.assertRaises(ValueError):
            server.collect_snapshot("host", FakeClient({}))

    def test_host_scope_reads_only_node_list_then_selected_node_status(self):
        client = FakeClient(
            {
                "nodes": {"data": [{"node": "pve1", "status": "online"}]},
                "node_status:pve1": {
                    "data": {
                        "uptime": 3600,
                        "cpu": 0.2,
                        "memory": {"total": 1000, "used": 400, "free": 600},
                    }
                },
            }
        )
        result = server.collect_host_snapshot("pve1", client)
        self.assertEqual(client.calls, ["nodes", "node_status:pve1"])
        self.assertEqual(result["scope"], "host")
        self.assertEqual(result["sources"]["membership"]["status"], "online")
        self.assertEqual(result["sources"]["node_status"]["uptime"], 3600)
        self.assertIn("estimated_boot_at", result["sources"]["node_status"])
        self.assertEqual(result["errors"], [])

    def test_host_scope_rejects_a_node_not_in_cluster_membership(self):
        client = FakeClient({"nodes": {"data": [{"node": "pve1", "status": "online"}]}})
        with self.assertRaisesRegex(ValueError, "not found"):
            server.collect_host_snapshot("pve2", client)
        self.assertEqual(client.calls, ["nodes"])

    def test_host_scope_reports_status_failure_without_claiming_host_is_down(self):
        client = FakeClient(
            {
                "nodes": {"data": [{"node": "pve1", "status": "online"}]},
                "node_status:pve1": server.ProxmoxApiError("PVE status request timed out."),
            }
        )
        result = server.collect_host_snapshot("pve1", client)
        self.assertEqual(result["sources"]["membership"]["status"], "online")
        self.assertNotIn("node_status", result["sources"])
        self.assertEqual(result["errors"][0]["source"], "node_status")


class HandlerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.web_dir = tempfile.TemporaryDirectory()
        web_root = Path(cls.web_dir.name)
        (web_root / "prototype").mkdir()
        (web_root / "docs" / "proxmox").mkdir(parents=True)
        (web_root / "index.html").write_text("<html>Home</html>", encoding="utf-8")
        (web_root / "prototype" / "index.html").write_text(
            "<html>Prototype</html>", encoding="utf-8"
        )
        (web_root / "docs" / "proxmox" / "A01.md").write_text(
            "# Kiểm tra node\n", encoding="utf-8"
        )
        cls.web_root_env = patch.dict(
            os.environ,
            {"PVE_DIAG_WEB_ROOT": cls.web_dir.name},
        )
        cls.web_root_env.start()
        cls.httpd = server.ThreadingHTTPServer(("127.0.0.1", 0), server.DiagnosticHandler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.httpd.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=2)
        cls.web_root_env.stop()
        cls.web_dir.cleanup()

    def post(self, body, authenticated=True, origin="http://127.0.0.1"):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=2)
        headers = {"Content-Type": "application/json", "Host": "127.0.0.1"}
        if authenticated:
            headers["X-Authenticated-User"] = "operator"
        if origin:
            headers["Origin"] = origin
        connection.request("POST", "/api/diagnose", body=json.dumps(body), headers=headers)
        response = connection.getresponse()
        payload = json.loads(response.read())
        connection.close()
        return response.status, payload

    def get(self, path, authenticated=True):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=2)
        headers = {"Host": "127.0.0.1"}
        if authenticated:
            headers["X-Authenticated-User"] = "operator"
        connection.request("GET", path, headers=headers)
        response = connection.getresponse()
        payload = response.read()
        content_type = response.getheader("Content-Type")
        status = response.status
        connection.close()
        return status, content_type, payload

    def test_static_pages_require_authentication(self):
        status, _, _ = self.get("/pve-diagnostic/prototype/", authenticated=False)
        self.assertEqual(status, 401)

    def test_markdown_is_served_as_utf8_markdown(self):
        status, content_type, payload = self.get(
            "/pve-diagnostic/docs/proxmox/A01.md"
        )
        self.assertEqual(status, 200)
        self.assertIn("text/markdown", content_type)
        self.assertIn("charset=utf-8", content_type)
        self.assertIn("Kiểm tra node".encode("utf-8"), payload)

    def test_requires_authenticated_operator(self):
        status, payload = self.post({"scope": "ceph"}, authenticated=False)
        self.assertEqual(status, 401)
        self.assertIn("authentication", payload["error"].lower())

    def test_rejects_cross_origin_request(self):
        status, payload = self.post({"scope": "ceph"}, origin="http://attacker.example")
        self.assertEqual(status, 403)
        self.assertIn("Cross-origin", payload["error"])

    @patch("prototype.server.collect_snapshot")
    def test_accepts_only_scope_and_never_forwards_incident_text(self, collect_snapshot):
        collect_snapshot.return_value = {
            "scope": "ceph",
            "collected_at": "2026-01-01T00:00:00+00:00",
            "sources": {"ceph": {"health": {"status": "HEALTH_OK"}}},
            "errors": [],
        }
        status, payload = self.post({"scope": "ceph"})
        self.assertEqual(status, 200)
        self.assertEqual(payload["sources"]["ceph"]["health"]["status"], "HEALTH_OK")
        collect_snapshot.assert_called_once_with("ceph")

    @patch("prototype.server.collect_snapshot")
    def test_rejects_incident_text_and_extra_body_fields(self, collect_snapshot):
        status, payload = self.post({"scope": "ceph", "issue": "secret incident details"})
        self.assertEqual(status, 400)
        self.assertIn("only the diagnostic scope", payload["error"])
        collect_snapshot.assert_not_called()

    @patch("prototype.server.collect_host_snapshot")
    def test_accepts_host_scope_with_a_node_name(self, collect_host_snapshot):
        collect_host_snapshot.return_value = {
            "scope": "host",
            "node": "pve1",
            "collected_at": "2026-01-01T00:00:00+00:00",
            "sources": {"membership": {"status": "online"}},
            "errors": [],
        }
        status, payload = self.post({"scope": "host", "node": "pve1"})
        self.assertEqual(status, 200)
        self.assertEqual(payload["node"], "pve1")
        collect_host_snapshot.assert_called_once_with("pve1")

    @patch("prototype.server.collect_host_snapshot")
    def test_rejects_arbitrary_host_path_and_extra_host_data(self, collect_host_snapshot):
        for body in (
            {"scope": "host", "node": "../cluster/status"},
            {"scope": "host", "node": "pve1", "issue": "private incident"},
        ):
            with self.subTest(body=body):
                status, _ = self.post(body)
                self.assertEqual(status, 400)
        collect_host_snapshot.assert_not_called()


if __name__ == "__main__":
    unittest.main()
