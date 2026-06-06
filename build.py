#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建脚本：将共享组件注入 HTML 文件，输出到 dist/"""
import os
import re
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

    # 图片
    if images and images[0]:
        img_html = f'<img src="{images[0]}" alt="{title}" style="width:100%;height:100%;object-fit:contain;">'
    else:
        # 无图片时用子分类首字或默认图标
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


def generate_cards_html(cat_name):
    """生成指定分类下所有产品卡片的 HTML"""
    products = load_products()
    cat_products = [p for p in products if p.get('cat') == cat_name]
    if not cat_products:
        return ''
    return '\n'.join(generate_card(p) for p in cat_products)


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

    # --- 确保 dist/ 存在 ---
    os.makedirs(DIST_DIR, exist_ok=True)

    # --- 复制静态资源 ---
    for dirname in ['images', 'data', 'fonts']:
        src = os.path.join('.', dirname)
        dst = os.path.join(DIST_DIR, dirname)
        if os.path.exists(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"[OK] 已复制 {src}/ -> {dst}/")

    # --- 收集 HTML 文件 ---
    html_files = []
    for f in os.listdir('.'):
        if f.endswith('.html') and os.path.isfile(f):
            html_files.append(f)
    html_files.sort()
    print(f"[INFO] 找到 {len(html_files)} 个 HTML 文件: {html_files}")

    # --- 处理每个 HTML 文件 ---
    for fname in html_files:
        content = read_file(fname)
        if not content:
            continue

        modified = False

        # 1. 替换 CSS 占位符: <!-- #include css:a,b,c --> → 内联 <style>
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

        # 2. 替换 JS 占位符: <!-- #include js:a,b,c --> → 内联 <script>
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

        # 3. 替换组件占位符: <!-- #include xxx.html -->
        for name in COMPONENTS:
            placeholder = f'<!-- #include {name}.html -->'
            if placeholder in new_content and components[name]:
                new_content = new_content.replace(placeholder, components[name])
                modified = True

        # 4. 替换产品卡片占位符: <!-- #include cards:分类名 -->
        def replace_cards(m):
            cat_name = m.group(1).strip()
            return generate_cards_html(cat_name)

        new_content2, n_cards = re.subn(
            r'<!--\s*#include\s+cards:(.+?)\s*-->', replace_cards, new_content
        )
        if n_cards:
            modified = True
        new_content = new_content2

        # 5. 替换版本号占位符
        if '{{BUILD_TIME}}' in new_content:
            new_content = new_content.replace('{{BUILD_TIME}}', build_time)
            modified = True

        # 6. 写入 dist/
        out_path = os.path.join(DIST_DIR, fname)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        if modified:
            print(f"[OK] {fname} -> dist/{fname} (CSSx{n_css}, JSx{n_js}, 卡片x{n_cards})")
        else:
            print(f"[SKIP] {fname} (无占位符)")

    print(f"\n[SUCCESS] 构建完成 @ {build_time}")
    print(f"[INFO] 输出目录: {DIST_DIR}/  |  产品总数: {len(products)}")


if __name__ == '__main__':
    build()
