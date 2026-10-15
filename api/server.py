import json
import os
import urllib.request
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

TICKETS = Path("/data/tickets.json")
DOC_ROOTS = {
    "docs": Path("/docs"),
    "runbooks": Path("/runbooks"),
    "postmortems": Path("/postmortems"),
    "evidence": Path("/evidence"),
}

def read_tickets():
    try:
        data = json.loads(TICKETS.read_text())
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("tickets", "incidents"):
                if isinstance(data.get(key), list):
                    return data[key]
            result = []
            for key, value in data.items():
                if isinstance(value, dict):
                    item = dict(value)
                    item.setdefault("id", key)
                    result.append(item)
            return result
    except (OSError, json.JSONDecodeError):
        pass
    return []

def all_documents():
    result = []
    for category, root in DOC_ROOTS.items():
        if root.exists():
            for path in sorted(root.rglob("*.md")):
                result.append({
                    "path": f"{category}/{path.relative_to(root)}",
                    "title": path.stem.replace("-", " ").replace("_", " ").title(),
                    "category": category,
                })
    return result

class Handler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/api/tickets":
            tickets = read_tickets()
            tickets.sort(key=lambda t: str(
                t.get("detected_at", t.get("created_at", ""))
            ), reverse=True)
            return self.send_json({"tickets": tickets})

        if parsed.path == "/api/health":
            try:
                req = urllib.request.Request(
                    os.environ.get("PORTAL_HEALTH_URL", "http://web/"),
                    headers={"User-Agent": "LSFL-Operations-Monitor"}
                )
                with urllib.request.urlopen(req, timeout=3) as response:
                    code = response.status
                return self.send_json({
                    "status": "healthy" if code == 200 else "unhealthy",
                    "http_code": code,
                    "service": "LSFL Customer Portal",
                })
            except Exception:
                return self.send_json({
                    "status": "unhealthy",
                    "http_code": 0,
                    "service": "LSFL Customer Portal",
                })

        if parsed.path == "/api/docs":
            requested = params.get("file", [None])[0]
            if not requested:
                return self.send_json({"documents": all_documents()})

            parts = requested.split("/", 1)
            if len(parts) != 2 or parts[0] not in DOC_ROOTS:
                return self.send_json({"error": "Document not found"}, 404)

            root = DOC_ROOTS[parts[0]].resolve()
            path = (root / parts[1]).resolve()
            if root not in path.parents or not path.is_file():
                return self.send_json({"error": "Document not found"}, 404)

            try:
                return self.send_json({
                    "path": requested,
                    "title": path.stem.replace("-", " ").title(),
                    "content": path.read_text(errors="replace"),
                })
            except OSError:
                return self.send_json({"error": "Unable to read document"}, 500)

        return self.send_json({"error": "Not found"}, 404)

    def log_message(self, fmt, *args):
        print("[LSFL API]", fmt % args)

print("LSFL API listening on port 8000")
ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8000"))), Handler).serve_forever()
