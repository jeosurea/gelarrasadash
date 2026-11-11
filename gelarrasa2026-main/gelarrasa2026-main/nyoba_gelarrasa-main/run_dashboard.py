#!/usr/bin/env python3
"""
Launcher script untuk AQMS Dashboard.
Menjalankan local HTTP server dan langsung membuka browser otomatis.
"""

import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def run():
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print("=" * 60)
        print("🍃 AQMS DASHBOARD NASIONAL BERHASIL DIJALANKAN!")
        print("=" * 60)
        print(f"URL: {url}")
        print("Tekan Ctrl+C di terminal ini jika ingin menghentikan server.")
        print("=" * 60)
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer dihentikan.")

if __name__ == '__main__':
    run()
