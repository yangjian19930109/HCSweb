#!/usr/bin/env python3
"""简单的 HTTP 服务器，确保正确的 Content-Type + charset"""
import http.server
import os
import sys

PORT = 8080
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist')

# MIME 类型映射，确保 text 类型带上 charset
MIME = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.xml': 'application/xml; charset=utf-8',
    '.svg': 'image/svg+xml; charset=utf-8',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.ico': 'image/x-icon',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.ttf': 'font/ttf',
    '.eot': 'application/vnd.ms-fontobject',
}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def guess_type(self, path):
        ext = os.path.splitext(path)[1].lower()
        return MIME.get(ext, 'application/octet-stream')

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")


if __name__ == '__main__':
    os.chdir(DIR)
    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'✅ 服务器已启动: http://0.0.0.0:{PORT}/')
    print(f'   静态文件目录: {DIR}')
    print(f'   Content-Type 已包含 charset=utf-8')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n服务器已停止')
        server.server_close()
