#!/usr/bin/env python3
"""
Overspire Local Web Playtest Server
Godot 4 Web(Wasm/Threads) 구동에 필수적인 COOP/COEP 헤더를 지원하는 로컬 웹 서버입니다.
사용법: python3 scripts/serve_web.py [포트번호] [웹디렉터리]
기본값: 포트 8060, 디렉터리 web_build
"""

import sys
import os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8060
WEB_DIR = sys.argv[2] if len(sys.argv) > 2 else "web_build"

class GodotWebHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Godot 4 WebAssembly 및 SharedArrayBuffer 지원 필수 헤더
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

def main():
    abs_web_dir = os.path.abspath(WEB_DIR)
    os.makedirs(abs_web_dir, exist_ok=True)
    os.chdir(abs_web_dir)
    server_address = ("0.0.0.0", PORT)
    httpd = ThreadingHTTPServer(server_address, GodotWebHandler)
    print(f"[Overspire Web Server] Running on http://localhost:{PORT}")
    print(f"[Overspire Web Server] Serving directory: {abs_web_dir}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Overspire Web Server] Stopped.")

if __name__ == "__main__":
    main()
