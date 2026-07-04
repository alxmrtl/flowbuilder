#!/usr/bin/env python3
"""Serves mockups/ and accepts POST /save from the Metrics System Workbench,
writing the spec to mockups/metrics-spec.json (validated before writing).
Run:  python3 tools/workbench-server.py
Open: http://localhost:8123/metrics-system-workbench.html"""
import http.server, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOCK = os.path.join(ROOT, "mockups")
SPEC = os.path.join(MOCK, "metrics-spec.json")

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=MOCK, **k)

    def do_GET(self):
        if self.path == "/ping":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
            return
        super().do_GET()

    def do_POST(self):
        if self.path != "/save":
            self.send_response(404); self.end_headers(); return
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        try:
            json.loads(body)
        except ValueError:
            self.send_response(400); self.end_headers()
            self.wfile.write(b"invalid json"); return
        with open(SPEC, "wb") as f:
            f.write(body)
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"saved")
        print("saved ->", SPEC)

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    print("Workbench at http://localhost:8123/metrics-system-workbench.html")
    http.server.ThreadingHTTPServer(("127.0.0.1", 8123), H).serve_forever()
