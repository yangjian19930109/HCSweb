#!/usr/bin/env python3
"""HTTP 服务器：静态文件 + 表单提交 API"""
import http.server
import os
import sys
import json
import smtplib
import uuid
from email.mime.text import MIMEText
from datetime import datetime

PORT = 8080
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist')

# SMTP 配置（通过环境变量设置）
SMTP_HOST = os.environ.get('SMTP_HOST', '')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '465'))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS', '')
SMTP_TO = os.environ.get('SMTP_TO', 'yangjian@motorp.cn')

# 数据存储目录
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

# MIME 类型映射
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


def send_email(name, phone, message):
    """通过 SMTP 发送邮件，返回 (success, error_message)"""
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS]):
        return False, 'SMTP 未配置'

    subject = f'[华创生官网] 新咨询 - {name}'
    body = f"""<h2>新的客户咨询</h2>
<table style="border-collapse:collapse;font-family:Arial,sans-serif">
<tr><td style="padding:8px 12px;background:#f0f0f0;font-weight:bold">姓名</td><td style="padding:8px 12px">{name}</td></tr>
<tr><td style="padding:8px 12px;background:#f0f0f0;font-weight:bold">电话</td><td style="padding:8px 12px">{phone}</td></tr>
<tr><td style="padding:8px 12px;background:#f0f0f0;font-weight:bold">留言</td><td style="padding:8px 12px">{message}</td></tr>
<tr><td style="padding:8px 12px;background:#f0f0f0;font-weight:bold">时间</td><td style="padding:8px 12px">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
</table>"""

    msg = MIMEText(body, 'html', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = SMTP_TO

    try:
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
            server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, [SMTP_TO], msg.as_string())
        server.quit()
        return True, None
    except Exception as e:
        return False, str(e)


def save_submission(data):
    """保存提交记录到本地 JSON 文件"""
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, 'submissions.json')
    records = []
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                records = json.load(f)
        except (json.JSONDecodeError, IOError):
            records = []
    records.append(data)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def guess_type(self, path):
        ext = os.path.splitext(path)[1].lower()
        return MIME.get(ext, 'application/octet-stream')

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/contact':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body)

                name = (data.get('name') or '').strip()
                phone = (data.get('phone') or '').strip()
                message = (data.get('message') or '').strip()

                # 校验
                errors = []
                if not name or len(name) > 50:
                    errors.append('姓名不能为空且不超过50字')
                if not phone or len(phone) < 7 or len(phone) > 20:
                    errors.append('请输入有效的电话号码')
                if not message or len(message) < 2 or len(message) > 2000:
                    errors.append('留言不能为空（2-2000字）')

                if errors:
                    self._json_response(400, {'ok': False, 'errors': errors})
                    return

                # 构建记录
                record = {
                    'id': uuid.uuid4().hex[:12],
                    'name': name,
                    'phone': phone,
                    'message': message,
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                }

                # 保存到本地文件
                save_submission(record)

                # 发送邮件
                email_ok, email_err = send_email(name, phone, message)

                if email_ok:
                    self._json_response(200, {'ok': True, 'msg': '提交成功，我们会尽快与您联系！'})
                elif email_err == 'SMTP 未配置':
                    # 即使没发邮件，本地已保存，也算成功
                    self._json_response(200, {'ok': True, 'msg': '提交成功，我们会尽快与您联系！'})
                else:
                    # 发邮件失败但本地已保存
                    print(f'[WARN] 邮件发送失败: {email_err}')
                    self._json_response(200, {'ok': True, 'msg': '提交成功，我们会尽快与您联系！'})

            except (json.JSONDecodeError, ValueError) as e:
                self._json_response(400, {'ok': False, 'errors': ['数据格式错误']})
            except Exception as e:
                print(f'[ERROR] {e}')
                self._json_response(500, {'ok': False, 'errors': ['服务器内部错误，请稍后重试']})
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def _json_response(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")


if __name__ == '__main__':
    os.chdir(DIR)
    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'✅ 服务器已启动: http://0.0.0.0:{PORT}/')
    print(f'   静态文件目录: {DIR}')
    print(f'   API 端点: POST /api/contact')
    if SMTP_HOST:
        print(f'   SMTP: {SMTP_HOST}:{SMTP_PORT} → {SMTP_TO}')
    else:
        print(f'   ⚠️  SMTP 未配置，表单提交仅保存到本地 data/submissions.json')
        print(f'   设置环境变量: SMTP_HOST SMTP_PORT SMTP_USER SMTP_PASS')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n服务器已停止')
        server.server_close()
