#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建脚本：将 inc/nav.html 合并到所有 HTML 文件的占位符位置"""
import os
import re
import shutil

INC_DIR = 'inc'
DIST_DIR = 'dist'
PLACEHOLDER = '<!-- #include nav.html -->'

def main():
    # 读取 inc/nav.html
    nav_path = os.path.join(INC_DIR, 'nav.html')
    if not os.path.exists(nav_path):
        print(f"[ERR] 未找到 {nav_path}")
        exit(1)
    
    with open(nav_path, 'r', encoding='utf-8') as f:
        nav_html = f.read()
    print(f"[OK] 已读取 {nav_path} ({len(nav_html)} 字符)")
    
    # 确保 dist 目录存在
    os.makedirs(DIST_DIR, exist_ok=True)
    
    # 复制静态资源目录到 dist/
    for dirname in ['images', 'data']:
        src = os.path.join('.', dirname)
        dst = os.path.join(DIST_DIR, dirname)
        if os.path.exists(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"[OK] 已复制 {src}/ -> {dst}/")
        else:
            print(f"[WARN] {src}/ 不存在，跳过")
    
    # 查找所有 HTML 文件（排除 dist/ 和备份文件）
    html_files = []
    for f in os.listdir('.'):
        if f.endswith('.html') and os.path.isfile(f):
            html_files.append(f)
    
    html_files.sort()
    print(f"[INFO] 找到 {len(html_files)} 个 HTML 文件: {html_files}")
    
    # 处理每个 HTML 文件
    for fname in html_files:
        with open(fname, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if PLACEHOLDER not in content:
            print(f"[WARN] {fname} 中未找到占位符，跳过")
            continue
        
        # 替换占位符
        new_content = content.replace(PLACEHOLDER, nav_html)
        
        # 写入 dist/
        out_path = os.path.join(DIST_DIR, fname)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        count = content.count(PLACEHOLDER)
        print(f"[OK] {fname} -> dist/{fname} (替换 {count} 处)")
    
    print(f"\n[SUCCESS] 构建完成！输出目录: {DIST_DIR}/")
    print(f"[INFO] 启动命令: python build.py && http-server {DIST_DIR}/ -p 8080")

if __name__ == '__main__':
    main()
