# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''YB-0044 mock commit service: stands in for an irreversible agent action. Listens on 127.0.0.1 only (reached from OpenShell
sandboxes through the loopback tunnel). Every request is appended to a JSON-lines log with its arrival time (time.time()).
POST /transfer {"task": ..., "amount": ...} -> 200 {"committed": true}; GET /health -> 200.
Usage: python3 agr/mock_commit_service.py <port> <log.jsonl>'''
import json, sys, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
PORT, LOG = int(sys.argv[1]), sys.argv[2]
class H(BaseHTTPRequestHandler):
    def _log(self, body):
        with open(LOG, 'a') as f: f.write(json.dumps(dict(t=time.time(), method=self.command, path=self.path, body=body)) + chr(10))
    def do_GET(self):
        self._log(None); self.send_response(200); self.end_headers(); self.wfile.write(b'ok')
    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0); raw = self.rfile.read(n).decode() if n else ''
        try: body = json.loads(raw) if raw else None
        except Exception: body = raw
        self._log(body); self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers()
        self.wfile.write(json.dumps(dict(committed=True)).encode())
    def log_message(self, *a): pass
ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
