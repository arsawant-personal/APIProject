#!/usr/bin/env python3
"""
Simple HTTP server for Unified Console
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()
PORT = 8082

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SCRIPT_DIR), **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

def main():
    """Start the HTTP server"""
    print("🚀 Unified Console Server starting...")
    print(f"📁 Serving files from: {SCRIPT_DIR}")
    print(f"🌐 Server will run at: http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Allow reuse of the address to prevent "Address already in use" errors
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            print(f"✅ Unified Console Server running at http://localhost:{PORT}")
            print(f"🌐 Open your browser and go to: http://localhost:{PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {PORT} is already in use")
            print("Please stop any existing server on this port")
        else:
            print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 