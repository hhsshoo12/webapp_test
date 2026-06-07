import http.server
import json
import socketserver
import os
import sys
import urllib.request

PORT = int(os.environ.get('PORT', 50050))
print(f"Using port from launcher: {PORT}")


def _notify_ready(port: int) -> None:
    """Signal the webapp-launcher port allocator that this backend is ready."""
    payload = json.dumps({"port": port}).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:51000/ready",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            print(f"[ready] Notified port allocator: port {port} is ready (status={resp.status})")
    except Exception as e:
        print(f"[ready] Could not notify port allocator (will fall back to socket detection): {e}")


# Simple HTTP request handler
class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>TestIsolatedApp</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f7f7f5;
            color: #37352f;
            margin: 0;
        }
        h1 {
            font-size: 32px;
            font-weight: 700;
        }
    </style>
</head>
<body>
    <h1>Hello World</h1>
</body>
</html>
"""
        self.wfile.write(html.encode("utf-8"))

print(f"Starting server on http://localhost:{PORT}")
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
    # Notify the launcher that this backend is now ready to accept connections
    _notify_ready(PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")
        sys.exit(0)
