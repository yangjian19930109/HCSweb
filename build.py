#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建脚本：将共享组件注入 HTML 文件，输出到 dist/"""
import os
import re
import shutil
from datetime import datetime

# --- 配置 ---
INC_DIR = 'inc'
DIST_DIR = 'dist'
CSS_DIR = 'css'
JS_DIR = 'js'

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


def build():
    build_time = datetime.now().strftime('v%Y.%m.%d-%H:%M')

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
    for dirname in ['images', 'data', 'css', 'js']:
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

        # 1. 替换 CSS 占位符: <!-- #include css:a,b,c -->
        def replace_css(m):
            names = [n.strip() for n in m.group(1).split(',')]
            links = []
            for n in names:
                if n in CSS_MAP:
                    links.append(f'<link rel="stylesheet" href="css/{CSS_MAP[n]}">')
            return '\n    '.join(links)

        new_content, n_css = re.subn(
            r'<!--\s*#include\s+css:(.+?)\s*-->', replace_css, content
        )
        if n_css:
            modified = True

        # 2. 替换 JS 占位符: <!-- #include js:a,b,c -->
        def replace_js(m):
            names = [n.strip() for n in m.group(1).split(',')]
            scripts = []
            for n in names:
                if n in JS_MAP:
                    scripts.append(f'<script src="js/{JS_MAP[n]}"></script>')
            return '\n    '.join(scripts)

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

        # 4. 替换版本号占位符
        if '{{BUILD_TIME}}' in new_content:
            new_content = new_content.replace('{{BUILD_TIME}}', build_time)
            modified = True

        # 5. 写入 dist/
        out_path = os.path.join(DIST_DIR, fname)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        if modified:
            print(f"[OK] {fname} -> dist/{fname} (CSSx{n_css}, JSx{n_js})")
        else:
            print(f"[SKIP] {fname} (无占位符)")

    print(f"\n[SUCCESS] 构建完成 @ {build_time}")
    print(f"[INFO] 输出目录: {DIST_DIR}/")


if __name__ == '__main__':
    build()
