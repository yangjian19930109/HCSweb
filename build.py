#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建脚本：将共享组件注入 HTML 文件，输出到 dist/"""
import os
import re
import sys

# 修复 Windows GBK 终端编码乱码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json
import shutil
import subprocess
from datetime import datetime

# --- 配置 ---
INC_DIR = 'inc'
DIST_DIR = 'dist'
CSS_DIR = 'css'
JS_DIR = 'js'
DATA_DIR = 'data'

# 组件 HTML 文件映射
COMPONENTS = ['nav', 'sidebar', 'footer']

# CSS 文件映射 (占位符名 -> css 文件名)
CSS_MAP = {
    'common': 'common.css',
    'nav': 'nav.css',
    'sidebar': 'sidebar.css',
    'footer': 'footer.css',
    'products': 'products.css',
    'product-detail': 'product-detail.css',
}

# JS 文件映射 (占位符名 -> js 文件名)
JS_MAP = {
    'common': 'common.js',
    'nav-search': 'nav-search.js',
    'sidebar': 'sidebar.js',
    'product-detail': 'product-detail.js',
}


def read_file(path):
    if not os.path.exists(path):
        print(f"[WARN] 未找到 {path}")
        return ''
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def load_products():
    """从 products.json 读取产品列表"""
    path = os.path.join(DATA_DIR, 'products.json')
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_card(product):
    """生成单个产品卡片的 HTML"""
    pid = product.get('id', '')
    title = product.get('title', '')
    desc = product.get('desc', '')
    subcat = product.get('subCat', '')
    url = product.get('url', '#')
    images = product.get('images', []) or []

    # 标签取自子分类
    tag_html = f'<span class="product-card-tag">{subcat}</span>' if subcat else ''

    # 图片（优先卡片图）
    card = product.get('cardImage', '')
    img_src = card if card else (images[0] if images else '')
    if img_src:
        img_html = f'<img src="{img_src}" alt="{title}" style="width:100%;height:100%;object-fit:contain;">'
    else:
        emoji = {
            '节气门马达': '⚡', '废气阀马达': '💨', '涡轮增压执行器马达': '🌀',
            '车门锁马达': '🔒', 'EPB马达': '🅿️', '其他马达': '⚙️',
            '家用电器马达': '🏠', '电动工具马达': '🔧',
            '微动开关': '🔘',
        }.get(subcat, '⚙️')
        img_html = emoji

    # 有独立详情页的用链接包裹
    if url and url.endswith('.html'):
        return (
            f'<a href="{url}" class="product-card-link">'
            f'<div class="product-card">'
            f'<div class="product-card-img">{img_html}</div>'
            f'<div class="product-card-body"><h3>{title}</h3><p>{desc}</p>{tag_html}</div>'
            f'</div></a>'
        )
    else:
        return (
            f'<div class="product-card">'
            f'<div class="product-card-img">{img_html}</div>'
            f'<div class="product-card-body"><h3>{title}</h3><p>{desc}</p>{tag_html}</div>'
            f'</div>'
        )


def generate_cards_html(filter_name):
    """生成指定分类/子分类下所有产品卡片的 HTML（优先匹配 cat，其次 subCat）"""
    products = load_products()
    filtered = [p for p in products if p.get('cat') == filter_name]
    if not filtered:
        filtered = [p for p in products if p.get('subCat') == filter_name]
    if not filtered:
        return ''
    return '\n'.join(generate_card(p) for p in filtered)


def process_includes(content, components, build_time):
    """处理所有 #include 占位符和 {{BUILD_TIME}}，返回处理后的内容"""
    modified = False

    # 1. 替换 CSS 占位符
    def replace_css(m):
        names = [n.strip() for n in m.group(1).split(',')]
        styles = []
        for n in names:
            if n in CSS_MAP:
                css_content = read_file(os.path.join(CSS_DIR, CSS_MAP[n]))
                if css_content:
                    styles.append(f'<style>\n{css_content}\n</style>')
        return '\n'.join(styles)

    new_content, n_css = re.subn(
        r'<!--\s*#include\s+css:(.+?)\s*-->', replace_css, content
    )
    if n_css:
        modified = True

    # 2. 替换 JS 占位符
    def replace_js(m):
        names = [n.strip() for n in m.group(1).split(',')]
        scripts = []
        for n in names:
            if n in JS_MAP:
                js_content = read_file(os.path.join(JS_DIR, JS_MAP[n]))
                if js_content:
                    scripts.append(f'<script>\n{js_content}\n</script>')
        return '\n'.join(scripts)

    new_content2, n_js = re.subn(
        r'<!--\s*#include\s+js:(.+?)\s*-->', replace_js, new_content
    )
    if n_js:
        modified = True
    new_content = new_content2

    # 3. 替换组件占位符
    for name in COMPONENTS:
        placeholder = f'<!-- #include {name}.html -->'
        if placeholder in new_content and components[name]:
            new_content = new_content.replace(placeholder, components[name])
            modified = True

    # 4. 替换产品卡片占位符
    def replace_cards(m):
        cat_name = m.group(1).strip()
        return generate_cards_html(cat_name)

    new_content2, n_cards = re.subn(
        r'<!--\s*#include\s+cards:(.+?)\s*-->', replace_cards, new_content
    )
    if n_cards:
        modified = True
    new_content = new_content2

    # 5. 替换版本号
    if '{{BUILD_TIME}}' in new_content:
        new_content = new_content.replace('{{BUILD_TIME}}', build_time)
        modified = True

    return new_content, modified, n_css, n_js, n_cards


def generate_product_detail(product, template, components, build_time):
    """从模板生成单个产品详情页"""
    pid = product.get('id', '')
    title = product.get('title', '')
    product_type = product.get('productType', '') or product.get('subCat', '')
    desc = product.get('desc', '')
    images = product.get('images', []) or []
    detail_images = product.get('detail_images', []) or []
    specs = product.get('specs', {})

    # 主图
    main_img = images[0] if images else ''

    # 缩略图（仅主图）
    thumbs = []
    for i, img in enumerate(images):
        active = ' active' if i == 0 else ''
        thumbs.append(f'<img src="{img}" alt="图{i+1}" class="thumb{active}">')
    thumbs_html = '\n'.join(thumbs) if thumbs else ''

    # 规格参数
    spec_rows = []
    for label, value in specs.items():
        spec_rows.append(f'<div class="spec-row"><span class="spec-label">{label}</span><span class="spec-value">{value}</span></div>')
    specs_html = '\n'.join(spec_rows) if spec_rows else ''

    # 详情图
    chart_imgs = []
    for img in detail_images:
        chart_imgs.append(f'<img src="{img}" alt="{title}详情图" class="chart-img">')
    chart_html = '\n'.join(chart_imgs) if chart_imgs else ''

    # 替换占位符
    content = template
    content = content.replace('{{PAGE_TITLE}}', title)
    content = content.replace('{{PRODUCT_TITLE}}', title)
    content = content.replace('{{PRODUCT_TAG}}', product_type)
    content = content.replace('{{PRODUCT_MODEL}}', pid)
    content = content.replace('{{PRODUCT_DESC}}', desc)
    content = content.replace('{{PRODUCT_MAIN_IMG}}', main_img)
    content = content.replace('{{PRODUCT_THUMBNAILS}}', thumbs_html)
    content = content.replace('{{PRODUCT_SPECS}}', specs_html)
    content = content.replace('{{PRODUCT_CHART_IMAGES}}', chart_html)

    # 处理 include 占位符
    content, _, n_css, n_js, _ = process_includes(content, components, build_time)
    return content, n_css, n_js


def build():
    build_time = datetime.now().strftime('v%Y.%m.%d-%H:%M')
    products = load_products()

    # --- 读取 HTML 组件 ---
    components = {}
    for name in COMPONENTS:
        path = os.path.join(INC_DIR, f'{name}.html')
        components[name] = read_file(path)
        if components[name]:
            print(f"[OK] 已读取 inc/{name}.html ({len(components[name])} 字符)")

    # --- 确保 dist/ 存在，清理旧数据文件 ---
    os.makedirs(DIST_DIR, exist_ok=True)
    old_data = os.path.join(DIST_DIR, 'data')
    if os.path.exists(old_data):
        shutil.rmtree(old_data)
        print(f"[OK] 已清理 dist/data/")

    # --- 复制静态资源（排除 data/ 避免泄露产品数据） ---
    for dirname in ['images', 'fonts']:
        src = os.path.join('.', dirname)
        dst = os.path.join(DIST_DIR, dirname)
        if os.path.exists(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"[OK] 已复制 {src}/ -> {dst}/")

    # --- 读取产品详情模板 ---
    template = read_file('product-detail-template.html')

    # --- 收集 HTML 文件（排除模板文件） ---
    html_files = []
    for f in os.listdir('.'):
        if f.endswith('.html') and os.path.isfile(f) and f != 'product-detail-template.html':
            html_files.append(f)
    html_files.sort()
    print(f"[INFO] 找到 {len(html_files)} 个页面文件: {html_files}")

    detail_count = 0

    # --- 处理每个 HTML 文件 ---
    for fname in html_files:
        content = read_file(fname)
        if not content:
            continue

        new_content, modified, n_css, n_js, n_cards = process_includes(content, components, build_time)

        # 写入 dist/
        out_path = os.path.join(DIST_DIR, fname)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        if modified:
            print(f"[OK] {fname} -> dist/{fname} (CSSx{n_css}, JSx{n_js}, 卡片x{n_cards})")
        else:
            print(f"[SKIP] {fname} (无占位符)")

    # --- 生成产品详情页 ---
    for p in products:
        url = p.get('url', '')
        if not url.endswith('.html'):
            continue
        fname = url  # e.g. "product-1030837.html"
        content, n_css, n_js = generate_product_detail(p, template, components, build_time)
        out_path = os.path.join(DIST_DIR, fname)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] 模板生成 {fname} (CSSx{n_css}, JSx{n_js})")
        detail_count += 1

    print(f"\n[SUCCESS] 构建完成 @ {build_time}")
    print(f"[INFO] 输出目录: {DIST_DIR}/  |  产品总数: {len(products)}  |  详情页: {detail_count}")


if __name__ == '__main__':
    build()
