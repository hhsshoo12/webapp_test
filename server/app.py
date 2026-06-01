# server/app.py - Simple HTTP Server that fetches port from the launcher port server
import http.server
import socketserver
import urllib.request
import os
import sys

# Get app name
APP_NAME = "TestIsolatedApp"

# Port server defaults
PORT_SERVER_URL = "http://127.0.0.1:23001/get-port"
PORT = 23050 # Default fallback

# Try fetching port from Launcher Port Server
try:
    home_dir = os.path.expanduser('~')
    token_file = os.path.join(home_dir, '.webapp', '.port_token')
    
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            token = f.read().strip()
        
        req = urllib.request.Request(f"{PORT_SERVER_URL}?app={APP_NAME}")
        req.add_header('Authorization', token)
        
        print("Requesting port allocation from Launcher port server...")
        with urllib.request.urlopen(req) as response:
            res_content = response.read().decode().strip()
            PORT = int(res_content)
            print(f"Allocated port: {PORT}")
    else:
        print("Port token file not found. Using default port.")
except Exception as e:
    print(f"Failed to obtain port from Launcher port server: {e}")
    print("Using default fallback port.")

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
