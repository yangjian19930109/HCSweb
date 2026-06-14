## 一、CSS/JS 内联构建

### 问题

重构将 CSS/JS 抽离为独立文件后，每个页面 6-10 个 HTTP 请求，国内环境加载慢。

### 方案

改 `build.py`，`<!-- #include css:... -->` 和 `<!-- #include js:... -->` 不再生成 `<link>`/`<script src>`，而是读取文件内容包进 `<style>`/`<script>` 标签。

```python
# CSS: 读取 css/*.css → <style>...</style>
def replace_css(m):
    styles = []
    for n in names:
        css_content = read_file(os.path.join(CSS_DIR, CSS_MAP[n]))
        if css_content:
            styles.append(f'<style>\n{css_content}\n</style>')
    return '\n'.join(styles)

# JS: 读取 js/*.js → <script>...</script>
def replace_js(m):
    scripts = []
    for n in names:
        js_content = read_file(os.path.join(JS_DIR, JS_MAP[n]))
        if js_content:
            scripts.append(f'<script>\n{js_content}\n</script>')
    return '\n'.join(scripts)
```

### 效果

- 每个页面从 6-10 个请求降到 2 个（HTML + Fuse CDN）
- 源码依然模块化，开发体验不变
- 构建后不需复制 css/js 目录到 dist

---

## 二、字体自托管

### 问题

Google Fonts（Orbitron + Share Tech Mono）在国内加载不稳定或无法加载，回退到系统宋体/新宋体，赛博朋克风格全丢。

### 方案

1. 从 fonts.gstatic.com 下载 TTF 文件到 `fonts/`
2. 写 `fonts/fonts.css` 声明 `@font-face`，指向本地 ttf
3. 页面 `<link>` 从 Google CDN 改为 `href="fonts/fonts.css"`
4. `build.py` 加 `fonts` 到复制目录列表
5. 总共 6 个字体文件约 130KB，浏览器永久缓存

### CSS 变量回退链

`common.css` 中的字体变量需要好的回退方案：

```css
/* 改前 — monospace 在 CJK Windows 上落到新宋体 */
--font-display: "Orbitron", monospace;
--font-body: "Share Tech Mono", monospace;

/* 改后 — Consolas 更接近数码风 */
--font-display: "Orbitron", "Microsoft YaHei", sans-serif;
--font-body: "Share Tech Mono", "Consolas", "Courier New", monospace;
```

**How to apply:** 国内部署的网站，Google Fonts 换成自托管。开源字体（OFL）可合法使用。
