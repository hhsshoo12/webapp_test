import http.server
import socketserver
import os
import sys

PORT = int(os.environ.get('PORT', 50050))
print(f"Using port from launcher: {PORT}")

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
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")
        sys.exit(0)
