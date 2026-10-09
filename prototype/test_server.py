import json
import http.client
import os
import ssl
import threading
import unittest
from io import BytesIO
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

    def test_rejects_unknown_endpoint(self):
        with self.assertRaises(server.ProxmoxApiError):
            self.client.get("/nodes/other/status")

    def test_rejects_plain_http_api_url(self):
        with patch.dict(os.environ, {"PVE_API_URL": "http://pve.example:8006"}):
            with self.assertRaises(server.ConfigurationError):
                server.api_url_from_env()


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


class CollectionTests(unittest.TestCase):
    def test_ceph_scope_reads_only_ceph_status(self):
        client = FakeClient({"ceph": {"data": {"health": {"status": "HEALTH_OK"}}}})
        result = server.collect_snapshot("ceph", client)
        self.assertEqual(client.calls, ["ceph"])
        self.assertEqual(result["sources"]["ceph"]["health"]["status"], "HEALTH_OK")
        self.assertIn("collected_at", result)

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


class HandlerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = server.ThreadingHTTPServer(("127.0.0.1", 0), server.DiagnosticHandler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.httpd.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=2)

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


if __name__ == "__main__":
    unittest.main()
