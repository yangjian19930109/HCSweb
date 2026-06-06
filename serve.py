#!/usr/bin/env python3
"""HTTP 服务器：静态文件 + 表单/产品 API"""
import http.server
import os
import sys
import json
import re
import smtplib
import subprocess
import uuid
from email.mime.text import MIMEText
from datetime import datetime

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(BASE_DIR, 'dist')
DATA_DIR = os.path.join(BASE_DIR, 'data')
ADMIN_DIR = os.path.join(BASE_DIR, 'backend')
IMAGES_DIR = os.path.join(BASE_DIR, 'images', 'products')
PRODUCTS_JSON = os.path.join(DATA_DIR, 'products.json')
PRODUCTS_JS = os.path.join(DATA_DIR, 'products.js')
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

# SMTP 配置（通过环境变量设置）
SMTP_HOST = os.environ.get('SMTP_HOST', '')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '465'))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS', '')
SMTP_TO = os.environ.get('SMTP_TO', 'yangjian@motorp.cn')

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

# 产品分类定义
CATEGORIES = [
    {"id": "car-motor", "name": "车用马达"},
    {"id": "appliance", "name": "家用电器及电动工具马达"},
    {"id": "switch", "name": "微动开关"},
]

SUBCATEGORIES = {
    "车用马达": ["节气门马达", "废气阀马达", "涡轮增压执行器马达", "车门锁马达", "EPB马达", "其他马达"],
    "家用电器及电动工具马达": ["家用电器马达", "电动工具马达"],
    "微动开关": ["微动开关"],
}

# 分类 → Tab 锚点映射
CAT_TAB_MAP = {
    "车用马达": "products.html#tab-motor",
    "家用电器及电动工具马达": "products.html#tab-appliance",
    "微动开关": "products.html#tab-switch",
}


def generate_url(pid, detail):
    """根据是否有详情自动生成产品链接"""
    if detail and detail.strip():
        return f"product-{pid}.html"
    return "products.html#tab-motor"


# ─── 产品数据操作 ───────────────────────────────────────────

def load_products():
    """从 products.json 读取产品列表"""
    if not os.path.exists(PRODUCTS_JSON):
        return []
    with open(PRODUCTS_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_products(products):
    """保存产品到 products.json，重新生成 JS，自动构建"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PRODUCTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    regenerate_js(products)
    # 自动重建静态页面
    auto_build()


def regenerate_js(products):
    """根据产品数据重新生成 products.js（保留尾部搜索函数）"""
    # 读取现有 products.js，提取尾部（搜索函数部分）
    tail = ''
    if os.path.exists(PRODUCTS_JS):
        with open(PRODUCTS_JS, 'r', encoding='utf-8') as f:
            content = f.read()
        # 找到 PRODUCTS_DATA 数组结束的 ];
        idx = content.index('var PRODUCTS_DATA = [')
        # 找到匹配的 ];
        depth = 0
        in_str = False
        sc = None
        i = idx
        while i < len(content):
            c = content[i]
            if in_str:
                if c == '\\' and i + 1 < len(content):
                    i += 1
                elif c == sc:
                    in_str = False
            else:
                if c in ('"', "'"):
                    in_str = True
                    sc = c
                elif c == '[':
                    depth += 1
                elif c == ']':
                    depth -= 1
                    if depth == 0:
                        # 找到 ];
                        j = i + 1
                        while j < len(content) and content[j] in ' \t':
                            j += 1
                        if j < len(content) and content[j] == ';':
                            tail = content[j + 1:]
                        else:
                            tail = content[i + 1:]
                        break
            i += 1

    # 生成产品数组
    lines = ['var PRODUCTS_DATA = [']
    for p in products:
        lines.append('    {')
        lines.append(f'        id: "{p["id"]}",')
        lines.append(f'        title: "{p["title"]}",')
        lines.append(f'        cat: "{p["cat"]}",')
        lines.append(f'        subCat: "{p["subCat"]}",')
        lines.append(f'        desc: "{p["desc"]}",')
        lines.append(f'        url: "{p["url"]}",')
        imgs = p.get('images', []) or []
        img_str = json.dumps(imgs, ensure_ascii=False)
        lines.append(f'        images: {img_str},')
        detail = p.get('detail', '') or ''
        lines.append(f'        detail: {json.dumps(detail, ensure_ascii=False)},')
        dimgs = p.get('detail_images', []) or []
        lines.append(f'        detail_images: {json.dumps(dimgs, ensure_ascii=False)}')
        lines.append('    },')
    lines.append('];')

    new_js = '\n'.join(lines) + '\n' + tail
    with open(PRODUCTS_JS, 'w', encoding='utf-8') as f:
        f.write(new_js)
    # 同时更新 dist
    dist_data = os.path.join(DIR, 'data')
    os.makedirs(dist_data, exist_ok=True)
    with open(os.path.join(dist_data, 'products.json'), 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)


def auto_build():
    """自动运行 build.py 重建静态页面"""
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(BASE_DIR, 'build.py')],
            cwd=BASE_DIR, capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print('[OK] 自动构建成功')
        else:
            print(f'[WARN] 自动构建失败:\n{result.stderr[:500]}')
    except Exception as e:
        print(f'[WARN] 自动构建异常: {e}')


# ─── 图片上传 ──────────────────────────────────────────────

def parse_multipart(body, boundary):
    """解析 multipart/form-data，返回 (fields, files)"""
    fields = {}
    files = []
    boundary_bytes = ('--' + boundary).encode('utf-8')
    parts = body.split(boundary_bytes)
    for part in parts:
        if not part or part in (b'--\r\n', b'--', b'\r\n'):
            continue
        if part[:2] == b'\r\n':
            part = part[2:]
        header_end = part.find(b'\r\n\r\n')
        if header_end == -1:
            continue
        headers_raw = part[:header_end].decode('utf-8', errors='replace')
        content = part[header_end + 4:]
        if content.endswith(b'\r\n'):
            content = content[:-2]
        m = re.search(r'Content-Disposition:\s*form-data;\s*name="([^"]+)"(?:\s*;\s*filename="([^"]*)")?', headers_raw, re.I)
        if not m:
            continue
        name = m.group(1)
        filename = m.group(2)
        if filename:
            files.append({'name': name, 'filename': filename, 'data': content})
        else:
            fields[name] = content.decode('utf-8', errors='replace')
    return fields, files


def save_uploaded_image(file_data, orig_filename, product_id):
    """保存上传的图片到 images/products/，返回相对路径"""
    ext = os.path.splitext(orig_filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        ext = '.jpg'
    safe_name = f"{product_id}_{uuid.uuid4().hex[:8]}{ext}"
    rel_path = f"images/products/{safe_name}"

    # 保存到项目目录
    proj_path = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(proj_path), exist_ok=True)
    with open(proj_path, 'wb') as f:
        f.write(file_data)

    # 同步到 dist
    dist_path = os.path.join(DIR, rel_path)
    os.makedirs(os.path.dirname(dist_path), exist_ok=True)
    with open(dist_path, 'wb') as f:
        f.write(file_data)

    return rel_path


# ─── SMTP 邮件 ──────────────────────────────────────────────

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


# ─── HTTP Handler ───────────────────────────────────────────

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
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    # ─── GET ─────────────────────────────────────────────

    def do_GET(self):
        # 管理后台
        if self.path == '/admin' or self.path.startswith('/admin/'):
            self._serve_admin()
            return

        # API: 产品列表
        if self.path == '/api/products':
            products = load_products()
            self._json_response(200, products)
            return

        # API: 搜索
        if self.path.startswith('/api/search'):
            from urllib.parse import urlparse, parse_qs
            pq = urlparse(self.path).query
            params = parse_qs(pq)
            q = (params.get('q', [''])[0] or '').strip()
            if not q:
                self._json_response(200, [])
                return
            q_lower = q.lower()
            products = load_products()
            hits = [
                {k: p[k] for k in ('id', 'title', 'cat', 'subCat', 'desc', 'url', 'images') if k in p}
                for p in products
                if q_lower in p.get('title', '').lower()
                or q_lower in p.get('desc', '').lower()
                or q_lower in p.get('subCat', '').lower()
            ][:10]
            self._json_response(200, hits)
            return

        # API: 分类列表
        if self.path == '/api/categories':
            cats = CATEGORIES.copy()
            for c in cats:
                c['subCategories'] = SUBCATEGORIES.get(c['name'], [])
            self._json_response(200, cats)
            return

        # 否则走静态文件
        super().do_GET()

    # ─── POST ────────────────────────────────────────────

    def do_POST(self):
        if self.path == '/api/contact':
            self._handle_contact()
        elif self.path == '/api/products':
            self._handle_add_product()
        elif self.path == '/api/products/batch-delete':
            self._handle_batch_delete()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    # ─── PUT ────────────────────────────────────────────

    def do_PUT(self):
        # /api/products/{id}
        m = re.match(r'^/api/products/(.+)$', self.path)
        if m:
            pid = m.group(1)
            self._handle_update_product(pid)
            return
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not Found')

    # ─── DELETE ──────────────────────────────────────────

    def do_DELETE(self):
        # /api/products/{id}
        m = re.match(r'^/api/products/(.+)$', self.path)
        if m:
            pid = m.group(1)
            products = load_products()
            before = len(products)
            products = [p for p in products if p.get('id') != pid]
            if len(products) == before:
                self._json_response(404, {'error': '产品不存在'})
                return
            save_products(products)
            self._json_response(200, {'ok': True})
            return
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not Found')

    # ─── 内部方法 ────────────────────────────────────────

    def _serve_admin(self):
        admin_file = os.path.join(ADMIN_DIR, 'admin.html')
        if not os.path.exists(admin_file):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Admin page not found')
            return
        with open(admin_file, 'r', encoding='utf-8') as f:
            html = f.read()
        body = html.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle_contact(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            name = (data.get('name') or '').strip()
            phone = (data.get('phone') or '').strip()
            message = (data.get('message') or '').strip()

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

            record = {
                'id': uuid.uuid4().hex[:12],
                'name': name,
                'phone': phone,
                'message': message,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
            save_submission(record)
            email_ok, email_err = send_email(name, phone, message)

            if email_ok:
                self._json_response(200, {'ok': True, 'msg': '提交成功，我们会尽快与您联系！'})
            else:
                if email_err != 'SMTP 未配置':
                    print(f'[WARN] 邮件发送失败: {email_err}')
                self._json_response(200, {'ok': True, 'msg': '提交成功，我们会尽快与您联系！'})
        except (json.JSONDecodeError, ValueError):
            self._json_response(400, {'ok': False, 'errors': ['数据格式错误']})
        except Exception as e:
            print(f'[ERROR] {e}')
            self._json_response(500, {'ok': False, 'errors': ['服务器内部错误，请稍后重试']})

    def _handle_add_product(self):
        try:
            content_type = self.headers.get('Content-Type', '')
            content_length = int(self.headers.get('Content-Length', 0))

            if 'multipart/form-data' in content_type:
                # 解析 multipart（含图片上传）
                m = re.search(r'boundary=([^\s;]+)', content_type)
                if not m:
                    self._json_response(400, {'ok': False, 'errors': ['无效的请求格式']})
                    return
                boundary = m.group(1).strip('"')
                body = self.rfile.read(content_length)
                fields, files = parse_multipart(body, boundary)

                pid = fields.get('id', '').strip()
                title = fields.get('title', '').strip()
                cat = fields.get('cat', '').strip()
                subCat = fields.get('subCat', '').strip()
                desc = fields.get('desc', '').strip()
                detail = fields.get('detail', '').strip()
                image_paths = []
                detail_image_paths = []
            else:
                # JSON 格式（兼容）
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body)
                pid = (data.get('id') or '').strip()
                title = (data.get('title') or '').strip()
                cat = (data.get('cat') or '').strip()
                subCat = (data.get('subCat') or '').strip()
                desc = (data.get('desc') or '').strip()
                detail = (data.get('detail') or '').strip()
                files = []
                image_paths = (data.get('images') or [])[:3]
                detail_image_paths = (data.get('detail_images') or [])

            errors = []
            if not pid:
                errors.append('产品ID不能为空')
            if not title:
                errors.append('产品名称不能为空')
            if not cat:
                errors.append('请选择分类')
            if not desc:
                errors.append('描述不能为空')

            if errors:
                self._json_response(400, {'ok': False, 'errors': errors})
                return

            products = load_products()
            if any(p.get('id') == pid for p in products):
                self._json_response(400, {'ok': False, 'errors': [f'产品ID "{pid}" 已存在']})
                return

            # 处理图片上传
            for f in files:
                if len(f['data']) > MAX_IMAGE_SIZE:
                    continue
                if not f['filename']:
                    continue
                path = save_uploaded_image(f['data'], f['filename'], pid)
                if f['name'].startswith('detail_'):
                    detail_image_paths.append(path)
                else:
                    if len(image_paths) < 3:
                        image_paths.append(path)

            url = generate_url(pid, detail)

            product = {
                'id': pid,
                'title': title,
                'cat': cat,
                'subCat': subCat,
                'desc': desc,
                'url': url,
                'images': image_paths,
                'detail': detail,
                'detail_images': detail_image_paths,
            }
            products.append(product)
            save_products(products)
            print(f'[OK] 新增产品: {pid} - {title} (图片: {len(image_paths)}张)')
            self._json_response(200, {'ok': True, 'product': product})
        except (json.JSONDecodeError, ValueError):
            self._json_response(400, {'ok': False, 'errors': ['数据格式错误']})
        except Exception as e:
            print(f'[ERROR] {e}')
            self._json_response(500, {'ok': False, 'errors': ['服务器内部错误']})

    def _handle_batch_delete(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            ids = data.get('ids', [])
            if not ids or not isinstance(ids, list):
                self._json_response(400, {'error': '请提供要删除的产品ID列表'})
                return
            products = load_products()
            before = len(products)
            products = [p for p in products if p.get('id') not in ids]
            deleted = before - len(products)
            save_products(products)
            print(f'[OK] 批量删除: {deleted} 个产品 (IDs: {ids})')
            self._json_response(200, {'ok': True, 'deleted': deleted})
        except (json.JSONDecodeError, ValueError):
            self._json_response(400, {'ok': False, 'errors': ['数据格式错误']})
        except Exception as e:
            print(f'[ERROR] {e}')
            self._json_response(500, {'ok': False, 'errors': ['服务器内部错误']})

    def _handle_update_product(self, pid):
        try:
            content_type = self.headers.get('Content-Type', '')
            content_length = int(self.headers.get('Content-Length', 0))

            if 'multipart/form-data' in content_type:
                m = re.search(r'boundary=([^\s;]+)', content_type)
                if not m:
                    self._json_response(400, {'ok': False, 'errors': ['无效的请求格式']})
                    return
                boundary = m.group(1).strip('"')
                body = self.rfile.read(content_length)
                fields, files = parse_multipart(body, boundary)

                title = fields.get('title', '').strip()
                cat = fields.get('cat', '').strip()
                subCat = fields.get('subCat', '').strip()
                desc = fields.get('desc', '').strip()
                detail = fields.get('detail', '').strip()
                keep_images = json.loads(fields.get('keep_images', '[]'))
                keep_detail_images = json.loads(fields.get('keep_detail_images', '[]'))
            else:
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body)
                title = (data.get('title') or '').strip()
                cat = (data.get('cat') or '').strip()
                subCat = (data.get('subCat') or '').strip()
                desc = (data.get('desc') or '').strip()
                detail = (data.get('detail') or '').strip()
                files = []
                keep_images = (data.get('keep_images') or [])
                keep_detail_images = (data.get('keep_detail_images') or [])

            products = load_products()
            idx = next((i for i, p in enumerate(products) if p.get('id') == pid), None)
            if idx is None:
                self._json_response(404, {'error': '产品不存在'})
                return

            product = products[idx]

            errors = []
            if not title:
                errors.append('产品名称不能为空')
            if not cat:
                errors.append('请选择分类')
            if not desc:
                errors.append('描述不能为空')

            if errors:
                self._json_response(400, {'ok': False, 'errors': errors})
                return

            # 保留的旧图片
            image_paths = keep_images[:3] if isinstance(keep_images, list) else []
            detail_image_paths = keep_detail_images[:5] if isinstance(keep_detail_images, list) else []

            # 处理新上传的图片
            for f in files:
                if len(f['data']) > MAX_IMAGE_SIZE:
                    continue
                if not f['filename']:
                    continue
                path = save_uploaded_image(f['data'], f['filename'], pid)
                if f['name'].startswith('detail_'):
                    if len(detail_image_paths) < 5:
                        detail_image_paths.append(path)
                else:
                    if len(image_paths) < 3:
                        image_paths.append(path)

            url = generate_url(pid, detail)

            products[idx] = {
                'id': pid,
                'title': title,
                'cat': cat,
                'subCat': subCat,
                'desc': desc,
                'url': url,
                'images': image_paths,
                'detail': detail,
                'detail_images': detail_image_paths,
            }
            save_products(products)
            print(f'[OK] 更新产品: {pid} - {title} (图片: {len(image_paths)}张)')
            self._json_response(200, {'ok': True, 'product': products[idx]})
        except (json.JSONDecodeError, ValueError):
            self._json_response(400, {'ok': False, 'errors': ['数据格式错误']})
        except Exception as e:
            print(f'[ERROR] {e}')
            self._json_response(500, {'ok': False, 'errors': ['服务器内部错误']})

    def _json_response(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")


# ─── 启动 ──────────────────────────────────────────────────

if __name__ == '__main__':
    # 如果 products.js 不存在，从 JSON 生成
    if not os.path.exists(PRODUCTS_JS):
        products = load_products()
        if products:
            regenerate_js(products)
            print(f'✅ 从 products.json 生成 products.js（{len(products)} 个产品）')

    os.chdir(DIR)
    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'✅ 服务器已启动: http://0.0.0.0:{PORT}/')
    print(f'   管理后台: http://0.0.0.0:{PORT}/admin')
    print(f'   API: POST /api/contact | GET/POST/DELETE /api/products')
    if SMTP_HOST:
        print(f'   SMTP: {SMTP_HOST}:{SMTP_PORT} → {SMTP_TO}')
    else:
        print(f'   ⚠️  SMTP 未配置，表单提交仅保存到本地')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n服务器已停止')
        server.server_close()
