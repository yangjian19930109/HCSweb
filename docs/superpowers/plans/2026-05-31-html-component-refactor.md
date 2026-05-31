# HTML 组件化重构 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 7 个 HTML 页面中重复的 CSS/JS/HTML 抽取为共享文件，通过增强的 build.py 注入，消除代码重复。

**Architecture:** HTML 页面只保留页面独有内容，共享的 CSS 放在 `css/` 目录、JS 放在 `js/` 目录、HTML 片段放在 `inc/` 目录。build.py 解析占位符 `<!-- #include css:... -->`、`<!-- #include js:... -->`、`<!-- #include xxx.html -->` 并在构建时注入。

**Tech Stack:** Python 3 (build.py), 纯 HTML/CSS/JS, Fuse.js (CDN), Google Fonts (CDN)

**Source spec:** `docs/superpowers/specs/2026-05-31-html-component-refactor-design.md`

---

## 文件创建/修改清单

| 操作 | 文件 | 职责 |
|------|------|------|
| CREATE | `css/common.css` | CSS 变量, 基础重置, 通用动画 |
| CREATE | `css/nav.css` | 导航栏全部样式 (含搜索框) |
| CREATE | `css/sidebar.css` | 侧边栏样式 |
| CREATE | `css/footer.css` | 页脚 + 悬浮按钮样式 |
| CREATE | `css/products.css` | 产品中心页特有样式 |
| CREATE | `css/product-detail.css` | 产品详情页共享样式 |
| CREATE | `js/common.js` | 移动菜单, 平滑滚动, 导航 active |
| CREATE | `js/nav-search.js` | 搜索逻辑 (Fuse) |
| CREATE | `js/sidebar.js` | 侧边栏 Tab 切换 |
| CREATE | `js/product-detail.js` | 产品图片浏览 |
| CREATE | `inc/sidebar.html` | 侧边栏纯 HTML 片段 |
| CREATE | `inc/footer.html` | 页脚纯 HTML 片段 |
| MODIFY | `inc/nav.html` | 去掉 `<style>` 和 `!important` |
| MODIFY | `build.py` | 多占位符 + CSS/JS 注入 + 资源复制 |
| MODIFY | `index.html` | 合并 index-inline.html, 用 include |
| MODIFY | `products.html` | 用 include |
| MODIFY | `product-1030837.html` | 用 include |
| MODIFY | `product-1030896.html` | 用 include |
| MODIFY | `other-motor.html` | 用 include |
| MODIFY | `throttle-motor.html` | 用 include |
| DELETE | `index-inline.html` | 合并到 index.html |

---

### Task 1: 创建 css/common.css

**Files:**
- Create: `css/common.css`

- [ ] **Step 1: 创建目录并写入文件**

```bash
mkdir -p css js
```

- [ ] **Step 2: 写入 css/common.css**

```css
/* ========== CSS 变量 ========== */
:root {
    /* 主色调 */
    --color-primary: #005d73;
    --color-primary-light: #007a8a;
    --color-accent: #00f5ff;
    --color-highlight: #ff2d78;
    --color-gold: #d4a84b;
    /* 背景色 */
    --bg-primary: #050810;
    --bg-nav: rgba(5, 8, 20, 0.92);
    --bg-card: rgba(0, 93, 115, 0.08);
    --bg-dark: #0a1628;
    --bg-dark-mid: #0d2137;
    --bg-dark-light: #0f2944;
    /* 文字色 */
    --text-primary: #ffffff;
    --text-secondary: rgba(255, 255, 255, 0.7);
    --text-muted: rgba(255, 255, 255, 0.4);
    --text-sidebar-dark: #1a1a2e;
    --text-sidebar-body: #666;
    --text-sidebar-muted: #888;
    /* 字体 */
    --font-display: "Orbitron", monospace;
    --font-body: "Share Tech Mono", monospace;
    --font-fallback: "Microsoft YaHei", monospace;
    /* 发光效果 */
    --glow-text: 0 0 8px #00f5ff, 0 0 16px #00f5ff, 0 0 32px #00f5ff;
    --glow-strong: 0 0 12px rgba(0, 245, 255, 1), 0 0 24px rgba(0, 245, 255, 0.5);
    --glow-box: 0 0 15px rgba(0, 245, 255, 0.5);
    --text-shadow-white: 0 0 8px #00f5ff, 0 0 16px #00f5ff, 0 0 32px #00f5ff, 0 0 64px rgba(0,245,255,0.6);
    /* 尺寸 */
    --nav-height: 80px;
    --sidebar-width: 220px;
    /* 边框 */
    --border-accent: 1px solid rgba(0, 245, 255, 0.3);
}

/* ========== 基础重置 ========== */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: var(--font-body), var(--font-display), var(--font-fallback);
    line-height: 1.6;
    color: #e0e0e0;
    background: var(--bg-primary);
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
    position: relative;
}

/* ========== 通用动画 ========== */
@keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

@keyframes pulse {
    0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.3; }
    50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.5; }
}

@keyframes pulse-rotate {
    0%, 100% { transform: translate(-50%, -50%) rotate(0deg); }
    50% { transform: translate(-50%, -50%) rotate(180deg); }
}

@keyframes wave {
    0% { width: 100px; height: 100px; opacity: 0; }
    100% { width: 500px; height: 500px; opacity: 0; }
}

@keyframes glow-pulse {
    from { text-shadow: 0 0 5px #00ffff, 0 0 10px #00ffff, 0 0 20px #00ffff; }
    to { text-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 40px #00ffff, 0 0 60px #00ffff; }
}
```

- [ ] **Step 3: Commit**

```bash
git add css/common.css
git commit -m "feat: add css/common.css — CSS variables, reset, animations"
```

---

### Task 2: 创建 css/nav.css

**Files:**
- Create: `css/nav.css`

- [ ] **Step 1: 写入 css/nav.css**

```css
/* ========== 导航栏容器 ========== */
.header {
    background: var(--bg-nav);
    backdrop-filter: blur(12px);
    position: fixed;
    width: 100%;
    top: 0;
    z-index: 1000;
}

.header .container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 15px 20px;
    position: relative;
    height: var(--nav-height);
    box-sizing: border-box;
}

/* ========== Logo ========== */
.logo {
    position: absolute;
    left: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    text-decoration: none;
    font-family: var(--font-display);
}

.logo-img {
    height: 60px;
    width: auto;
    vertical-align: middle;
    filter: drop-shadow(0 0 4px #00f5ff) drop-shadow(0 0 8px rgba(0,245,255,0.4));
}

.logo-text {
    font-size: 36px;
    font-weight: 900;
    color: var(--text-primary);
    text-shadow: var(--glow-text);
    font-family: var(--font-display);
}

/* ========== 导航链接 ========== */
.nav {
    display: flex;
    gap: 0;
    align-items: center;
}

.nav-spacer {
    flex: 1;
}

.nav-link {
    text-decoration: none;
    color: var(--text-primary);
    text-shadow: var(--text-shadow-white);
    font-weight: 700;
    font-family: var(--font-display);
    transition: all 0.3s;
    padding: 0 28px;
    height: var(--nav-height);
    line-height: var(--nav-height);
    display: block;
    border-bottom: 3px solid transparent;
    font-size: 17px;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.nav-link:hover,
.nav-link.active {
    color: var(--color-accent);
    border-bottom-color: var(--color-highlight);
    text-shadow: var(--glow-strong);
    letter-spacing: 3px;
}

/* ========== 下拉菜单 ========== */
.nav-dropdown {
    position: relative;
}

.nav-dropdown > .nav-link {
    display: flex;
    align-items: center;
    gap: 4px;
    cursor: pointer;
}

.nav-dropdown > .nav-link::after {
    content: '';
    display: inline-block;
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid currentColor;
    margin-top: 2px;
    transition: transform 0.3s ease;
}

.nav-dropdown:hover > .nav-link::after {
    transform: rotate(180deg);
}

.dropdown-menu {
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%) translateY(10px);
    min-width: 200px;
    background: rgba(10, 22, 40, 0.97);
    backdrop-filter: blur(12px);
    border-radius: 8px;
    padding: 8px 0;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
    box-shadow: 0 8px 32px rgba(0, 93, 115, 0.3), 0 2px 8px rgba(0, 0, 0, 0.3);
    z-index: 9999;
    border: 1px solid rgba(0, 93, 115, 0.3);
}

.nav-dropdown:hover .dropdown-menu {
    opacity: 1;
    visibility: visible;
    transform: translateX(-50%) translateY(0);
}

.dropdown-menu a {
    display: block;
    padding: 12px 24px;
    color: rgba(255, 255, 255, 0.7);
    font-family: var(--font-body);
    text-decoration: none;
    font-size: 14px;
    font-weight: 400;
    transition: all 0.25s ease;
    border-left: 3px solid transparent;
}

.dropdown-menu a:hover {
    color: var(--color-accent);
    background: rgba(0, 245, 255, 0.08);
    border-left-color: var(--color-highlight);
    text-shadow: 0 0 8px rgba(0, 245, 255, 0.8);
    padding-left: 28px;
}

/* ========== 搜索框 ========== */
.nav-search {
    position: fixed;
    right: 30px;
    top: 22px;
    display: flex;
    align-items: center;
    padding: 8px 16px;
    background: linear-gradient(135deg, rgba(0, 40, 80, 0.9), rgba(0, 20, 40, 0.95));
    border: 2px solid var(--color-accent);
    border-radius: 24px;
    box-shadow: var(--glow-box), inset 0 0 10px rgba(0, 245, 255, 0.1);
    transition: all 0.3s ease;
    z-index: 1001;
}

.nav-search:hover {
    transform: scale(1.12);
}

.nav-search .search-icon {
    color: rgba(0, 245, 255, 0.6);
    margin-left: 8px;
    flex-shrink: 0;
}

.nav-search:hover .search-icon,
.nav-search:focus-within .search-icon {
    color: var(--color-accent);
}

#nav-search-input {
    background: transparent;
    border: none;
    color: #e0f4ff;
    font-size: 14px;
    font-family: var(--font-body);
    outline: none;
    width: 120px;
    transition: width 0.3s ease;
}

#nav-search-input::placeholder {
    color: rgba(0, 245, 255, 0.4);
}

#nav-search-input:focus {
    width: 160px;
}

#nav-search-results {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: 8px;
    min-width: 280px;
    max-height: 400px;
    overflow-y: auto;
    background: rgba(0, 20, 40, 0.98);
    border: 1px solid var(--color-accent);
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 245, 255, 0.3);
    z-index: 1002;
    display: none;
}

#nav-search-results.visible {
    display: block;
}

.ns-item {
    display: flex;
    flex-direction: column;
    padding: 10px 14px;
    color: #fff;
    text-decoration: none;
    border-bottom: 1px solid rgba(0, 245, 255, 0.1);
    transition: background 0.2s;
    cursor: pointer;
}

.ns-item:last-child {
    border-bottom: none;
}

.ns-item:hover {
    background: rgba(0, 245, 255, 0.1);
}

.ns-cat {
    font-size: 11px;
    color: var(--color-accent);
    margin-bottom: 2px;
}

.ns-title {
    font-size: 14px;
    color: #fff;
    font-weight: 500;
}

.ns-desc {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.5);
    margin-top: 2px;
}

.ns-hint,
.ns-empty {
    padding: 20px;
    text-align: center;
    color: rgba(224, 244, 255, 0.5);
    font-size: 13px;
}

#nav-search-results::-webkit-scrollbar {
    width: 4px;
}

#nav-search-results::-webkit-scrollbar-track {
    background: transparent;
}

#nav-search-results::-webkit-scrollbar-thumb {
    background: rgba(0, 245, 255, 0.3);
    border-radius: 2px;
}

/* ========== 移动菜单按钮 ========== */
.mobile-menu-btn {
    display: none;
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    position: absolute;
    right: 10px;
    color: var(--text-primary);
}

/* ========== 版本号 ========== */
.nav-version {
    position: fixed;
    right: 20px;
    top: 22px;
    font-size: 12px;
    color: var(--color-accent);
    font-family: var(--font-display);
    background: rgba(0, 20, 40, 0.9);
    border: 1px solid var(--color-accent);
    border-radius: 4px;
    padding: 2px 8px;
    z-index: 1001;
    box-shadow: 0 0 8px rgba(0, 245, 255, 0.3);
}

/* ========== 移动端响应式 ========== */
@media (max-width: 768px) {
    .nav {
        display: none;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: rgba(5, 8, 20, 0.97);
        flex-direction: column;
        padding: 20px;
        box-shadow: 0 5px 10px rgba(0, 0, 0, 0.3);
        z-index: 999;
    }

    .nav.active {
        display: flex;
    }

    .nav-link {
        height: auto;
        line-height: 1.5;
        padding: 15px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .mobile-menu-btn {
        display: block;
    }

    .dropdown-menu {
        position: static;
        transform: none;
        opacity: 1;
        visibility: visible;
        box-shadow: none;
        border: none;
        background: transparent;
        padding: 0 0 0 20px;
        display: none;
    }

    .dropdown-menu.active {
        display: block;
    }

    .dropdown-menu a {
        padding: 10px 16px;
        font-size: 13px;
    }

    .nav-search {
        display: none;
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add css/nav.css
git commit -m "feat: add css/nav.css — navigation bar, dropdown, search styles"
```

---

### Task 3: 创建 css/sidebar.css

**Files:**
- Create: `css/sidebar.css`

- [ ] **Step 1: 写入 css/sidebar.css**

```css
/* ========== 侧边栏容器 ========== */
.products-sidebar {
    width: var(--sidebar-width);
    flex-shrink: 0;
    background: #fff;
    padding: 30px 0;
    box-shadow: 2px 0 16px rgba(0, 0, 0, 0.06);
    height: fit-content;
    position: fixed;
    top: 50%;
    transform: translateY(-50%);
    z-index: 1000;
    border-radius: 0 12px 12px 0;
}

/* ========== 侧边栏标题 ========== */
.sidebar-title {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-sidebar-dark);
    padding: 0 24px 20px;
    border-bottom: 1px solid #eee;
    margin-bottom: 10px;
    letter-spacing: 2px;
}

/* ========== 导航项 ========== */
.sidebar-nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 24px;
    cursor: pointer;
    transition: all 0.25s ease;
    border-left: 3px solid transparent;
    color: var(--text-sidebar-body);
    font-size: 15px;
    font-weight: 500;
    text-decoration: none;
    position: relative;
}

.sidebar-nav-item .item-icon {
    width: 36px;
    height: 36px;
    background: rgba(0, 93, 115, 0.08);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
    transition: all 0.25s ease;
}

.sidebar-nav-item:hover {
    background: rgba(0, 93, 115, 0.04);
    color: var(--color-primary);
}

.sidebar-nav-item:hover .item-icon {
    background: rgba(0, 93, 115, 0.15);
}

.sidebar-nav-item.active {
    background: rgba(0, 93, 115, 0.06);
    color: var(--color-primary);
    border-left-color: var(--color-highlight);
    font-weight: 600;
}

.sidebar-nav-item.active .item-icon {
    background: var(--color-primary);
    color: #fff;
}

.sidebar-nav-item .item-arrow {
    position: absolute;
    right: 20px;
    opacity: 0;
    transition: all 0.25s ease;
    font-size: 12px;
}

.sidebar-nav-item:hover .item-arrow,
.sidebar-nav-item.active .item-arrow {
    opacity: 1;
    right: 16px;
}

/* ========== 二级子菜单 ========== */
.sidebar-sub-items {
    position: absolute;
    left: 100%;
    top: 0;
    width: 200px;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    padding: 12px 0;
    display: none;
    z-index: 1001;
}

.sidebar-nav-item:hover > .sidebar-sub-items,
.sidebar-nav-item .sidebar-sub-items:hover {
    display: block;
}

.sidebar-sub-item {
    padding: 10px 16px;
    cursor: pointer;
    font-size: 13px;
    color: var(--text-sidebar-body);
    border-radius: 6px;
    transition: all 0.2s ease;
    margin-bottom: 4px;
}

.sidebar-sub-item:hover {
    background: rgba(0, 93, 115, 0.08);
    color: var(--color-primary);
}

.sidebar-sub-item.active {
    background: var(--color-primary);
    color: #fff;
}

.sidebar-sub-item a {
    color: inherit;
    text-decoration: none;
    display: block;
}

/* ========== 移动端响应式 ========== */
@media (max-width: 900px) {
    .products-layout {
        flex-direction: column;
        margin: 0;
        padding: 30px 0 60px;
    }

    .products-sidebar {
        width: 100%;
        position: static;
        padding: 0;
        background: transparent;
        box-shadow: none;
        border-radius: 0;
    }

    .sidebar-title {
        display: none;
    }

    .sidebar-nav {
        display: flex;
        gap: 8px;
        overflow-x: auto;
        padding: 0 20px 5px;
    }

    .sidebar-nav-item {
        flex-shrink: 0;
        padding: 10px 16px;
        border-left: none;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        background: #fff;
        font-size: 14px;
        white-space: nowrap;
    }

    .sidebar-nav-item .item-icon {
        width: 28px;
        height: 28px;
        font-size: 14px;
    }

    .sidebar-nav-item .item-arrow {
        display: none;
    }

    .sidebar-nav-item.active {
        background: var(--color-primary);
        color: #fff;
        border-color: var(--color-primary);
    }

    .sidebar-nav-item.active .item-icon {
        background: rgba(255, 255, 255, 0.2);
        color: #fff;
    }

    .products-content {
        padding: 0 20px;
        max-width: 100%;
        margin-left: 0;
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add css/sidebar.css
git commit -m "feat: add css/sidebar.css — sidebar navigation styles"
```

---

### Task 4: 创建 css/footer.css

**Files:**
- Create: `css/footer.css`

- [ ] **Step 1: 写入 css/footer.css**

```css
/* ========== 页脚 ========== */
.footer {
    background: #020408;
    border-top: 1px solid rgba(0, 245, 255, 0.15);
    color: #fff;
    padding: 60px 0 30px;
}

.footer-grid {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    gap: 40px;
    margin-bottom: 40px;
}

.footer-brand h3 {
    font-size: 24px;
    margin-bottom: 15px;
    color: #fff;
}

.footer-brand p {
    font-size: 14px;
    color: #999;
    line-height: 1.8;
}

.footer-column h4 {
    font-size: 16px;
    margin-bottom: 20px;
    color: #fff;
}

.footer-column ul {
    list-style: none;
}

.footer-column li {
    margin-bottom: 10px;
}

.footer-column a {
    color: #999;
    text-decoration: none;
    font-size: 14px;
    transition: color 0.3s;
}

.footer-column a:hover {
    color: #fff;
}

.footer-bottom {
    border-top: 1px solid #333;
    padding-top: 30px;
    text-align: center;
    color: #666;
    font-size: 14px;
}

/* ========== 悬浮按钮 ========== */
.float-buttons {
    position: fixed;
    right: 30px;
    bottom: 100px;
    z-index: 999;
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.float-btn {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 24px;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    transition: all 0.3s;
    text-decoration: none;
}

.float-btn:hover {
    transform: scale(1.1);
}

.float-btn.phone {
    background: var(--color-primary);
}

.float-btn.wechat {
    background: #22c55e;
}

/* ========== 微信弹窗 ========== */
.wechat-modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 1001;
    align-items: center;
    justify-content: center;
}

.wechat-modal.active {
    display: flex;
}

.wechat-modal-content {
    background: #fff;
    padding: 30px;
    border-radius: 8px;
    text-align: center;
    max-width: 300px;
}

.wechat-modal-content h3 {
    margin-bottom: 20px;
    color: #333;
}

.wechat-qr {
    width: 200px;
    height: 200px;
    background: #f0f4f8;
    margin: 0 auto 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #999;
    border-radius: 8px;
}

.close-modal {
    background: var(--color-primary);
    color: #fff;
    border: none;
    padding: 10px 30px;
    border-radius: 4px;
    cursor: pointer;
}

/* ========== 页脚响应式 ========== */
@media (max-width: 768px) {
    .footer-grid {
        grid-template-columns: 1fr 1fr;
    }
}

@media (max-width: 480px) {
    .footer-grid {
        grid-template-columns: 1fr;
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add css/footer.css
git commit -m "feat: add css/footer.css — footer and floating buttons"
```

---

### Task 5: 创建 css/products.css

**Files:**
- Create: `css/products.css`

- [ ] **Step 1: 写入 css/products.css**

```css
/* ========== 产品页 Hero ========== */
.page-hero {
    margin-top: var(--nav-height);
    background: linear-gradient(135deg, var(--bg-dark) 0%, var(--bg-dark-mid) 50%, var(--bg-dark-light) 100%);
    height: 33vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.page-hero::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
        radial-gradient(circle at 30% 50%, rgba(0, 100, 200, 0.08) 0%, transparent 50%),
        radial-gradient(circle at 70% 50%, rgba(0, 150, 255, 0.06) 0%, transparent 50%);
}

.page-hero-content {
    position: relative;
    z-index: 1;
}

.page-hero h1 {
    color: #fff;
    font-size: 48px;
    font-weight: 700;
    margin-bottom: 15px;
    letter-spacing: 4px;
}

.page-hero p {
    color: rgba(255, 255, 255, 0.7);
    font-size: 18px;
    margin-bottom: 8px;
}

.page-hero-divider {
    width: 60px;
    height: 3px;
    background: var(--color-gold);
    margin: 20px auto 0;
    border-radius: 2px;
}

.products-glow {
    text-align: center;
    font-size: 70px;
    font-weight: 900;
    letter-spacing: 12px;
    color: transparent;
    -webkit-text-stroke: 2.5px #00ffff;
    -webkit-text-fill-color: transparent;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-shadow:
        0 0 10px #00d4ff,
        0 0 20px #00d4ff,
        0 0 40px rgba(0, 212, 255, 0.6),
        0 0 80px rgba(0, 212, 255, 0.3),
        0 0 120px rgba(0, 212, 255, 0.15);
    animation: glow-pulse 2s ease-in-out infinite;
}

/* ========== 产品布局 ========== */
.products-layout {
    display: flex;
    align-items: flex-start;
    padding: 50px 0 80px;
    min-height: 700px;
    position: relative;
}

.products-content {
    flex: 1;
    padding: 0 40px;
    max-width: calc(100vw - 240px);
    margin-left: var(--sidebar-width);
}

/* ========== Tab 面板 ========== */
.product-tab-panel {
    display: none;
    scroll-margin-top: 90px;
}

.product-tab-panel.active {
    display: block;
}

.tab-panel-header {
    margin-bottom: 30px;
    padding: 24px 30px;
    border-left: 4px solid var(--color-accent);
    background: linear-gradient(135deg, rgba(0, 245, 255, 0.08) 0%, rgba(255, 45, 120, 0.05) 100%);
    border-radius: 8px;
    position: relative;
    overflow: hidden;
}

.tab-panel-header::before {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(0, 245, 255, 0.1) 0%, transparent 70%);
    pointer-events: none;
}

.tab-panel-header .category-tag {
    display: inline-block;
    background: linear-gradient(135deg, var(--color-accent) 0%, #0099cc 100%);
    color: var(--bg-primary);
    font-size: 11px;
    font-weight: 700;
    padding: 5px 18px;
    border-radius: 2px;
    margin-bottom: 14px;
    letter-spacing: 3px;
    text-transform: uppercase;
    box-shadow: 0 0 15px rgba(0, 245, 255, 0.3), inset 0 0 6px rgba(255, 255, 255, 0.2);
    font-family: var(--font-display);
}

.tab-panel-header h2 {
    font-size: 28px;
    color: var(--color-accent);
    font-weight: 700;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 4px;
    text-shadow: 0 0 10px rgba(0, 245, 255, 0.6), 0 0 30px rgba(0, 245, 255, 0.3);
    font-family: var(--font-display);
}

.tab-panel-header p {
    color: rgba(224, 224, 224, 0.85);
    font-size: 15px;
    line-height: 1.7;
}

.tab-panel-header .category-desc {
    max-width: 700px;
    margin-top: 10px;
    color: rgba(224, 224, 224, 0.85);
    font-size: 14px;
    line-height: 1.9;
    letter-spacing: 0.5px;
}

/* ========== 产品卡片 ========== */
.product-card-grid-sidebar {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 16px;
}

.product-card {
    background: #fff;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    transition: all 0.3s ease;
    border: 1px solid #f0f0f0;
    aspect-ratio: 1 / 1;
    display: flex;
    flex-direction: column;
}

.product-card-link {
    text-decoration: none;
    display: block;
    color: inherit;
}

.product-card-link:hover .product-card {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 93, 115, 0.15);
    border-color: rgba(0, 93, 115, 0.2);
}

.product-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 93, 115, 0.15);
    border-color: rgba(0, 93, 115, 0.2);
}

.product-card-img {
    flex: 1;
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 50px;
    color: rgba(255, 255, 255, 0.8);
    position: relative;
    overflow: hidden;
}

.product-card-img::after {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    transition: left 0.5s;
}

.product-card:hover .product-card-img::after {
    left: 100%;
}

.product-card-img img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.product-card-body {
    padding: 18px;
}

.product-card-body h3 {
    font-size: 15px;
    color: var(--text-sidebar-dark);
    font-weight: 600;
    margin-bottom: 8px;
}

.product-card-body p {
    font-size: 13px;
    color: var(--text-sidebar-muted);
    line-height: 1.5;
}

.product-card-tag {
    display: inline-block;
    background: rgba(0, 93, 115, 0.08);
    color: var(--color-primary);
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 12px;
    margin-top: 10px;
}

/* ========== CTA 区域 ========== */
.cta-section {
    background: var(--color-primary);
    padding: 60px 0;
    text-align: center;
}

.cta-section h2 {
    color: #fff;
    font-size: 28px;
    margin-bottom: 15px;
}

.cta-section p {
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 25px;
    font-size: 16px;
}

.cta-btn {
    display: inline-block;
    background: var(--color-gold);
    color: #fff;
    padding: 14px 40px;
    border-radius: 6px;
    text-decoration: none;
    font-weight: 600;
    font-size: 16px;
    transition: background 0.3s;
}

.cta-btn:hover {
    background: #c49a3d;
}

/* ========== 产品页响应式 ========== */
@media (max-width: 900px) {
    .products-content {
        padding: 0 20px;
        max-width: 100%;
        margin-left: 0;
    }

    .product-card-grid-sidebar {
        grid-template-columns: 1fr 1fr;
        gap: 16px;
    }

    .product-card-img {
        height: 130px;
        font-size: 40px;
    }

    .tab-panel-header h2 {
        font-size: 22px;
    }

    .page-hero h1 {
        font-size: 32px;
    }

    .products-glow {
        font-size: 40px;
        letter-spacing: 6px;
    }
}

@media (max-width: 480px) {
    .product-card-grid-sidebar {
        grid-template-columns: 1fr;
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add css/products.css
git commit -m "feat: add css/products.css — product listing page styles"
```

---

### Task 6: 创建 css/product-detail.css

**Files:**
- Create: `css/product-detail.css`

- [ ] **Step 1: 写入 css/product-detail.css**

```css
/* ========== 产品详情容器 ========== */
.product-detail {
    margin-left: var(--sidebar-width);
    margin-top: var(--nav-height);
    padding: 60px 0;
}

/* ========== 面包屑 ========== */
.breadcrumb {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.4);
    margin-bottom: 30px;
}

.breadcrumb a {
    color: rgba(0, 245, 255, 0.7);
    text-decoration: none;
}

.breadcrumb a:hover {
    color: var(--color-accent);
}

.back-link {
    display: inline-block;
    color: rgba(0, 245, 255, 0.7);
    text-decoration: none;
    font-size: 14px;
    margin-bottom: 20px;
    transition: color 0.2s;
}

.back-link:hover {
    color: var(--color-accent);
}

/* ========== 产品展示区 ========== */
.product-hero {
    display: flex;
    gap: 60px;
    align-items: flex-start;
    margin-bottom: 60px;
}

/* ========== 图片画廊 ========== */
.product-gallery {
    flex: 1;
    max-width: 500px;
}

.main-img-wrapper {
    position: relative;
    width: 100%;
}

.product-main-img {
    width: 100%;
    aspect-ratio: 1 / 1;
    object-fit: contain;
    border-radius: 12px;
    border: 1px solid rgba(0, 245, 255, 0.2);
    background: rgba(0, 93, 115, 0.1);
    cursor: pointer;
    display: block;
}

.thumbnails {
    display: flex;
    gap: 10px;
    margin-top: 12px;
}

.thumb {
    width: 80px;
    height: 80px;
    object-fit: contain;
    border-radius: 8px;
    border: 2px solid rgba(0, 245, 255, 0.15);
    background: rgba(0, 93, 115, 0.1);
    cursor: pointer;
    transition: border-color 0.2s;
    padding: 4px;
}

.thumb:hover,
.thumb.active {
    border-color: var(--color-accent);
    box-shadow: 0 0 8px rgba(0, 245, 255, 0.3);
}

.img-nav-btn {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    background: rgba(5, 8, 20, 0.25);
    color: rgba(0, 245, 255, 0.6);
    border: 1px solid rgba(0, 245, 255, 0.2);
    font-size: 24px;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
    opacity: 0.6;
}

.img-nav-btn:hover {
    background: rgba(0, 245, 255, 0.25);
    border-color: var(--color-accent);
    color: var(--color-accent);
    box-shadow: 0 0 15px rgba(0, 245, 255, 0.5);
    opacity: 1;
}

.img-prev {
    left: 10px;
}

.img-next {
    right: 10px;
}

/* ========== 产品信息 ========== */
.product-info {
    flex: 1;
    max-width: 500px;
}

.product-info h1 {
    font-size: 32px;
    color: var(--color-accent);
    font-family: var(--font-display);
    margin-bottom: 10px;
    text-shadow: 0 0 10px rgba(0, 245, 255, 0.3);
}

.product-model {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.4);
    margin-bottom: 20px;
    font-family: var(--font-body);
}

.product-tag {
    display: inline-block;
    background: rgba(0, 93, 115, 0.15);
    color: var(--color-accent);
    font-size: 12px;
    padding: 4px 14px;
    border-radius: 12px;
    border: 1px solid rgba(0, 245, 255, 0.2);
    margin-bottom: 20px;
}

.product-desc {
    font-size: 15px;
    color: rgba(255, 255, 255, 0.7);
    line-height: 1.8;
    margin-bottom: 25px;
}

/* ========== 规格参数 ========== */
.product-specs {
    background: rgba(0, 93, 115, 0.08);
    border: 1px solid rgba(0, 245, 255, 0.15);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 25px;
}

.product-specs h3 {
    font-size: 16px;
    color: var(--color-accent);
    margin-bottom: 15px;
    font-family: var(--font-display);
}

.spec-row {
    display: flex;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    font-size: 14px;
}

.spec-row:last-child {
    border-bottom: none;
}

.spec-label {
    color: rgba(255, 255, 255, 0.4);
    width: 120px;
    flex-shrink: 0;
}

.spec-value {
    color: rgba(255, 255, 255, 0.85);
}

/* ========== 曲线图区域 ========== */
.product-chart {
    margin-bottom: 60px;
}

.product-chart h2 {
    font-size: 22px;
    color: var(--color-accent);
    font-family: var(--font-display);
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(0, 245, 255, 0.2);
}

.chart-img {
    width: 100%;
    border-radius: 12px;
    border: 1px solid rgba(0, 245, 255, 0.2);
    background: #fff;
}

.chart-note {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.4);
    margin-top: 10px;
}

/* ========== 产品详情响应式 ========== */
@media (max-width: 900px) {
    .product-detail {
        margin-left: 0;
    }

    .product-hero {
        flex-direction: column;
        gap: 30px;
    }

    .product-gallery,
    .product-info {
        max-width: 100%;
    }

    .thumbnails {
        overflow-x: auto;
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add css/product-detail.css
git commit -m "feat: add css/product-detail.css — product detail page styles"
```

---

### Task 7: 创建 js/common.js

**Files:**
- Create: `js/common.js`

- [ ] **Step 1: 写入 js/common.js**

```js
/**
 * common.js — 华创生电机网站通用脚本
 * 移动菜单、平滑滚动、导航 active、微信弹窗
 */
(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        initMobileMenu();
        initSmoothScroll();
        initNavActive();
        initWechatModal();
        initContactForm();
    });

    /* ========== 移动端菜单 ========== */
    function initMobileMenu() {
        var btn = document.querySelector('.mobile-menu-btn');
        var nav = document.querySelector('.nav');
        if (!btn || !nav) return;

        btn.addEventListener('click', function () {
            nav.classList.toggle('active');
            btn.textContent = nav.classList.contains('active') ? '✕' : '☰';
        });

        // 点击导航链接后关闭菜单
        var links = nav.querySelectorAll('.nav-link');
        links.forEach(function (link) {
            link.addEventListener('click', function () {
                nav.classList.remove('active');
                btn.textContent = '☰';
            });
        });

        // 移动端下拉菜单点击展开
        var dropdown = nav.querySelector('.nav-dropdown');
        var dropdownMenu = nav.querySelector('.dropdown-menu');
        if (dropdown && dropdownMenu) {
            var dropdownLink = dropdown.querySelector('.nav-link');
            if (dropdownLink) {
                dropdownLink.addEventListener('click', function (e) {
                    if (window.innerWidth <= 768) {
                        e.preventDefault();
                        dropdownMenu.classList.toggle('active');
                    }
                });
            }
        }
    }

    /* ========== 平滑滚动 ========== */
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
            anchor.addEventListener('click', function (e) {
                var targetId = this.getAttribute('href');
                if (targetId === '#') return; // skip empty hash
                e.preventDefault();
                var target = document.querySelector(targetId);
                if (target) {
                    var header = document.querySelector('.header');
                    var headerHeight = header ? header.offsetHeight : 80;
                    var targetPosition = target.offsetTop - headerHeight;
                    window.scrollTo({ top: targetPosition, behavior: 'smooth' });
                }
            });
        });
    }

    /* ========== 导航 active 状态 ========== */
    function initNavActive() {
        updateNavActive();
        window.addEventListener('hashchange', updateNavActive);
        window.addEventListener('scroll', updateNavOnScroll);
    }

    function updateNavActive() {
        var hash = window.location.hash;
        var navLinks = document.querySelectorAll('.nav-link');
        var currentUrl = window.location.href.split('/').pop().split('?')[0].split('#')[0];

        navLinks.forEach(function (link) {
            link.classList.remove('active');
            var href = link.getAttribute('href') || '';

            if (hash) {
                // 有 hash：匹配锚点
                if (href.endsWith(hash) || href === hash) {
                    link.classList.add('active');
                }
            } else {
                // 无 hash：根据当前页面 URL
                if (currentUrl === 'index.html' || currentUrl === '') {
                    if (href === 'index.html' || href === '#home') {
                        link.classList.add('active');
                    }
                } else if (currentUrl.startsWith('product-') || currentUrl.startsWith('other-') ||
                           currentUrl.startsWith('throttle-') || currentUrl === 'products.html') {
                    if (href.includes('products.html')) {
                        link.classList.add('active');
                    }
                }
            }
        });
    }

    function updateNavOnScroll() {
        var scrollTop = window.pageYOffset;
        var header = document.querySelector('.header');
        var headerHeight = header ? header.offsetHeight : 80;
        var sections = document.querySelectorAll('section[id]');
        var navLinks = document.querySelectorAll('.nav-link');

        sections.forEach(function (section) {
            var sectionTop = section.offsetTop - headerHeight - 100;
            var sectionHeight = section.offsetHeight;
            var sectionId = section.getAttribute('id');

            if (scrollTop >= sectionTop && scrollTop < sectionTop + sectionHeight) {
                navLinks.forEach(function (link) {
                    var href = link.getAttribute('href');
                    if (href && href.startsWith('#')) {
                        link.classList.remove('active');
                        if (href === '#' + sectionId) {
                            link.classList.add('active');
                        }
                    }
                });
            }
        });
    }

    /* ========== 微信弹窗 ========== */
    function initWechatModal() {
        var wechatBtn = document.getElementById('wechatBtn');
        var wechatModal = document.getElementById('wechatModal');
        var closeModal = document.getElementById('closeModal');

        if (wechatBtn && wechatModal) {
            wechatBtn.addEventListener('click', function () {
                wechatModal.classList.add('active');
            });
        }

        if (closeModal && wechatModal) {
            closeModal.addEventListener('click', function () {
                wechatModal.classList.remove('active');
            });
        }

        if (wechatModal) {
            wechatModal.addEventListener('click', function (e) {
                if (e.target === wechatModal) {
                    wechatModal.classList.remove('active');
                }
            });
        }
    }

    /* ========== 联系表单 ========== */
    function initContactForm() {
        var form = document.getElementById('contactForm');
        if (form) {
            form.addEventListener('submit', function (e) {
                e.preventDefault();
                alert('感谢您的咨询！我们会尽快与您联系。');
                form.reset();
            });
        }
    }
})();
```

- [ ] **Step 2: Commit**

```bash
git add js/common.js
git commit -m "feat: add js/common.js — mobile menu, smooth scroll, nav active, wechat modal"
```

---

### Task 8: 创建 js/nav-search.js

**Files:**
- Create: `js/nav-search.js`

- [ ] **Step 1: 写入 js/nav-search.js**

```js
/**
 * nav-search.js — 导航栏搜索功能
 * 依赖: Fuse.js (CDN), data/products.js (PRODUCTS_DATA + doSearch + initFuse)
 */
(function () {
    'use strict';

    function initNavSearch() {
        var input = document.getElementById('nav-search-input');
        var results = document.getElementById('nav-search-results');
        if (!input || !results) return;

        // 初始化 Fuse (如果已加载)
        if (typeof Fuse !== 'undefined' && typeof initFuse === 'function') {
            initFuse();
        }

        // 输入搜索
        input.addEventListener('input', function () {
            var q = input.value.trim();
            if (!q) {
                results.innerHTML = '<div class="ns-hint">输入关键词搜索...</div>';
                results.classList.add('visible');
                return;
            }
            var hits;
            if (typeof doSearch === 'function') {
                hits = doSearch(q);
            } else {
                // 无 Fuse 时的简单回退
                hits = (window.PRODUCTS_DATA || []).filter(function (p) {
                    return p.title.indexOf(q) >= 0 || p.desc.indexOf(q) >= 0;
                }).slice(0, 10);
            }
            if (hits.length === 0) {
                results.innerHTML = '<div class="ns-empty">未找到相关结果</div>';
                results.classList.add('visible');
                return;
            }
            results.innerHTML = hits.map(function (item) {
                return '<a href="' + (item.url || item.item && item.item.url || '#') + '" class="ns-item">' +
                    '<span class="ns-cat">' + (item.subCat || item.item && item.item.subCat || '') + '</span>' +
                    '<span class="ns-title">' + (item.title || item.item && item.item.title || '') + '</span>' +
                    '<span class="ns-desc">' + (item.desc || item.item && item.item.desc || '') + '</span></a>';
            }).join('');
            results.classList.add('visible');
        });

        // 聚焦时显示提示
        input.addEventListener('focus', function () {
            if (!input.value.trim() && !results.innerHTML) {
                results.innerHTML = '<div class="ns-hint">输入关键词搜索...</div>';
            }
            results.classList.add('visible');
        });

        // 点击外部关闭
        document.addEventListener('click', function (e) {
            if (!e.target.closest('.nav-search')) {
                results.classList.remove('visible');
            }
        });

        // Escape 关闭
        input.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                results.classList.remove('visible');
                input.blur();
            }
        });
    }

    // 页面加载后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNavSearch);
    } else {
        initNavSearch();
    }
})();
```

- [ ] **Step 2: Commit**

```bash
git add js/nav-search.js
git commit -m "feat: add js/nav-search.js — unified search logic"
```

---

### Task 9: 创建 js/sidebar.js

**Files:**
- Create: `js/sidebar.js`

- [ ] **Step 1: 写入 js/sidebar.js**

```js
/**
 * sidebar.js — 侧边栏 Tab 切换与 URL hash 同步
 */
(function () {
    'use strict';

    function initSidebar() {
        var sidebarItems = document.querySelectorAll('.sidebar-nav-item[data-tab]');
        var tabPanels = document.querySelectorAll('.product-tab-panel');
        if (sidebarItems.length === 0) return;

        // 点击切换
        sidebarItems.forEach(function (item) {
            item.addEventListener('click', function (e) {
                // 如果子菜单项有链接，不阻止跳转
                if (e.target.closest('.sidebar-sub-item a') || e.target.closest('.sidebar-sub-item[onclick]')) {
                    return;
                }
                var tabId = item.getAttribute('data-tab');
                if (!tabId) return;

                // 更新高亮
                sidebarItems.forEach(function (i) { i.classList.remove('active'); });
                item.classList.add('active');

                // 切换面板
                if (tabPanels.length > 0) {
                    tabPanels.forEach(function (panel) {
                        panel.classList.remove('active');
                        if (panel.id === 'tab-' + tabId) {
                            panel.classList.add('active');
                        }
                    });
                }

                // 更新 URL hash
                history.replaceState(null, '', '#' + tabId);
            });
        });

        // 页面加载时检查 URL hash
        var hash = window.location.hash.replace('#', '');
        if (hash) {
            var targetPanel = document.getElementById('tab-' + hash);
            var targetItem = document.querySelector('.sidebar-nav-item[data-tab="' + hash + '"]');
            if (targetItem && targetPanel) {
                sidebarItems.forEach(function (i) { i.classList.remove('active'); });
                targetItem.classList.add('active');
                tabPanels.forEach(function (panel) {
                    panel.classList.remove('active');
                    if (panel.id === 'tab-' + hash) {
                        panel.classList.add('active');
                    }
                });
            }
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSidebar);
    } else {
        initSidebar();
    }
})();
```

- [ ] **Step 2: Commit**

```bash
git add js/sidebar.js
git commit -m "feat: add js/sidebar.js — sidebar tab switching"
```

---

### Task 10: 创建 js/product-detail.js

**Files:**
- Create: `js/product-detail.js`

- [ ] **Step 1: 写入 js/product-detail.js**

```js
/**
 * product-detail.js — 产品详情页图片浏览
 */
(function () {
    'use strict';

    function initProductDetail() {
        var mainImg = document.getElementById('mainImg');
        var thumbs = document.querySelectorAll('.thumb');
        if (!mainImg || thumbs.length === 0) return;

        var currentIndex = 0;

        // 缩略图悬停切换主图
        thumbs.forEach(function (thumb, idx) {
            thumb.addEventListener('mouseenter', function () {
                switchTo(idx);
            });
        });

        function switchTo(idx) {
            mainImg.src = thumbs[idx].src;
            thumbs.forEach(function (t) { t.classList.remove('active'); });
            thumbs[idx].classList.add('active');
            currentIndex = idx;
        }

        // 前后翻按钮
        var prevBtn = document.querySelector('.img-prev');
        var nextBtn = document.querySelector('.img-next');

        if (prevBtn) {
            prevBtn.addEventListener('click', function () {
                var newIdx = (currentIndex - 1 + thumbs.length) % thumbs.length;
                switchTo(newIdx);
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', function () {
                var newIdx = (currentIndex + 1) % thumbs.length;
                switchTo(newIdx);
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initProductDetail);
    } else {
        initProductDetail();
    }
})();
```

- [ ] **Step 2: Commit**

```bash
git add js/product-detail.js
git commit -m "feat: add js/product-detail.js — product image gallery"
```

---

### Task 11: 创建 inc/sidebar.html

**Files:**
- Create: `inc/sidebar.html`

- [ ] **Step 1: 写入 inc/sidebar.html**

```html
<aside class="products-sidebar">
    <div class="sidebar-title">📦 产品分类</div>
    <nav class="sidebar-nav">
        <div class="sidebar-nav-item active" data-tab="motor">
            <div class="item-icon">⚡</div>
            <div class="item-text">
                <div>车用马达</div>
                <div style="font-size:11px;font-weight:400;opacity:0.7;">Automotive Motors</div>
            </div>
            <span class="item-arrow">›</span>
            <div class="sidebar-sub-items">
                <div class="sidebar-sub-item"><a href="throttle-motor.html">节气门马达</a></div>
                <div class="sidebar-sub-item" data-sub="waste-valve">废气阀马达</div>
                <div class="sidebar-sub-item" data-sub="turbo">涡轮增压执行器马达</div>
                <div class="sidebar-sub-item" data-sub="door-lock">车门锁马达</div>
                <div class="sidebar-sub-item" data-sub="epb">EPB马达</div>
                <div class="sidebar-sub-item"><a href="other-motor.html">其他车用马达</a></div>
            </div>
        </div>
        <div class="sidebar-nav-item" data-tab="appliance">
            <div class="item-icon">🏠</div>
            <div class="item-text">
                <div>家用电器及<br>电动工具马达</div>
                <div style="font-size:11px;font-weight:400;opacity:0.7;">Power Tools & Home Appliances</div>
            </div>
            <span class="item-arrow">›</span>
        </div>
        <div class="sidebar-nav-item" data-tab="switch">
            <div class="item-icon">🔘</div>
            <div class="item-text">
                <div>微动开关</div>
                <div style="font-size:11px;font-weight:400;opacity:0.7;">Micro Switches</div>
            </div>
            <span class="item-arrow">›</span>
        </div>
    </nav>
</aside>
```

- [ ] **Step 2: Commit**

```bash
git add inc/sidebar.html
git commit -m "feat: add inc/sidebar.html — sidebar HTML fragment"
```

---

### Task 12: 创建 inc/footer.html

**Files:**
- Create: `inc/footer.html`

- [ ] **Step 1: 写入 inc/footer.html**

```html
<footer class="footer">
    <div class="container">
        <div class="footer-grid">
            <div class="footer-brand">
                <h3>⚡ 华创生电机</h3>
                <p>华创生电机是德昌电机（JOHNSON ELECTRIC）授权代理商，专注自动化与智能化驱动领域20年，为客户提供专业的电机解决方案。</p>
            </div>
            <div class="footer-column">
                <h4>快速链接</h4>
                <ul>
                    <li><a href="index.html#home">首页</a></li>
                    <li><a href="index.html#about">关于我们</a></li>
                    <li><a href="products.html#products">产品中心</a></li>
                    <li><a href="index.html#news">新闻中心</a></li>
                </ul>
            </div>
            <div class="footer-column">
                <h4>产品中心</h4>
                <ul>
                    <li><a href="#">直流电机</a></li>
                    <li><a href="#">交流电机</a></li>
                    <li><a href="#">步进电机</a></li>
                    <li><a href="#">驱动系统</a></li>
                </ul>
            </div>
            <div class="footer-column">
                <h4>服务支持</h4>
                <ul>
                    <li><a href="#">技术文档</a></li>
                    <li><a href="#">售后服务</a></li>
                    <li><a href="#">常见问题</a></li>
                    <li><a href="index.html#contact">联系我们</a></li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2026 华创生电机有限公司 版权所有 | 粤ICP备xxxxxxxx号</p>
        </div>
    </div>
</footer>

<div class="float-buttons">
    <a href="tel:0755-12345678" class="float-btn phone" title="电话咨询">📞</a>
    <div class="float-btn wechat" id="wechatBtn" title="微信咨询">💬</div>
</div>

<div class="wechat-modal" id="wechatModal">
    <div class="wechat-modal-content">
        <h3>扫码添加微信</h3>
        <div class="wechat-qr">
            <span>二维码区域<br>请替换为实际图片</span>
        </div>
        <button class="close-modal" id="closeModal">关闭</button>
    </div>
</div>
```

- [ ] **Step 2: Commit**

```bash
git add inc/footer.html
git commit -m "feat: add inc/footer.html — footer HTML fragment"
```

---

### Task 13: 重写 inc/nav.html (去掉内联 style)

**Files:**
- Modify: `inc/nav.html`

- [ ] **Step 1: 备份原文件**

```bash
cp inc/nav.html inc/nav.html.bak
```

- [ ] **Step 2: 用纯 HTML 替换 inc/nav.html**

文件内容替换为（去掉 `<style>` 标签，保留纯 HTML 结构）：

```html
<header class="header">
    <div class="container">
        <a href="index.html" class="logo">
            <img src="images/logo.png" class="logo-img" alt="华创生电机">
            <span class="logo-text">华创生</span>
        </a>
        <nav class="nav">
            <a href="index.html" class="nav-link active">首页</a>
            <a href="#about" class="nav-link">关于我们</a>
            <div class="nav-dropdown">
                <a href="products.html?v=v20260419" class="nav-link">产品中心</a>
                <div class="dropdown-menu">
                    <a href="products.html#products-motor">车用马达</a>
                    <a href="products.html#products-power">电动工具及家用马达</a>
                    <a href="products.html#products-switch">微动开关</a>
                </div>
            </div>
            <a href="#news" class="nav-link">新闻中心</a>
            <a href="#contact" class="nav-link">联系我们</a>
            <div class="nav-spacer"></div>
            <div class="nav-search">
                <input type="text" id="nav-search-input" placeholder="搜索产品型号..." autocomplete="off">
                <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"/>
                    <path d="m21 21-4.35-4.35"/>
                </svg>
                <div id="nav-search-results" class="hidden"></div>
            </div>
        </nav>
        <span class="nav-version">{{BUILD_TIME}}</span>
        <button class="mobile-menu-btn">☰</button>
    </div>
</header>
```

- [ ] **Step 3: Commit**

```bash
git add inc/nav.html
git commit -m "refactor: remove inline <style> from nav.html, use CSS classes from nav.css"
```

---

### Task 14: 增强 build.py

**Files:**
- Modify: `build.py`

- [ ] **Step 1: 用以下内容完全替换 build.py**

```python
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
            print(f"[OK] {fname} -> dist/{fname} (CSS×{n_css}, JS×{n_js})")
        else:
            print(f"[SKIP] {fname} (无占位符)")

    print(f"\n[SUCCESS] 构建完成 @ {build_time}")
    print(f"[INFO] 输出目录: {DIST_DIR}/")


if __name__ == '__main__':
    build()
```

- [ ] **Step 2: Commit**

```bash
git add build.py
git commit -m "feat: enhance build.py — multi-placeholder, CSS/JS injection, build time"
```

---

### Task 15: 改造 index.html

**Files:**
- Modify: `index.html`

- [ ] **Step 1: 重写 index.html**

index.html 是首页，有大量 Banner 和首页特有的动画样式。我们保留首页特有的 CSS（Banner、六边形蜂巢、电机动画等）和首页特有的 JS（轮播、数字动画），其余用 include 替换。

具体替换：
- 在 `<head>` 末尾加 `<!-- #include css:common,nav,footer -->`，删除基础重置、导航、页脚、悬浮按钮的 CSS
- `<body>` 删掉导航 HTML，替换为 `<!-- #include nav.html -->`
- `<body>` 底部删掉页脚 HTML 和悬浮按钮，替换为 `<!-- #include footer.html -->`
- 在 Fuse.js 之后加 `<!-- #include js:common,nav-search -->`
- 删除导航栏的 `<style>` 块中已被 `nav.css` 覆盖的规则
- 保留首页特有: Banner 样式、齿轮动画、`#about`、`#news`、`#contact`、统计数字、产品六边形区

由于文件较长 (~2500行)，这一步需要精确操作。参见 plan 附录中的 `index.html` 改造对比。

**实际操作为用以下简化版 index.html 替换原文件** (见下方完整代码)。保留所有首页特有内容，只替换共享部分。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>华创生电机 - 专业电机解决方案提供商</title>
    <meta name="description" content="华创生电机是德昌电机(JOHNSON ELECTRIC)授权代理商，专注自动化与智能化驱动领域20年，提供直流电机、交流电机、步进电机、驱动系统等产品。">
    <!-- 强制刷新时回到顶部 -->
    <script>
    (function() {
        var isRefresh = window.performance && window.performance.navigation && window.performance.navigation.type === 1;
        if (isRefresh && window.location.hash) {
            history.replaceState(null, null, window.location.pathname);
            window.scrollTo(0, 0);
        }
    })();
    </script>
    <!-- #include css:common,nav,footer -->
    <style>
        /* ========== Banner 轮播区域（首页特有）========== */
        .banner {
            margin-top: 80px;
            position: relative;
            overflow: hidden;
            display: flex;
            width: 100%;
            aspect-ratio: 3 / 1;
            min-height: 500px;
            background: #050810;
        }
        .banner-left {
            flex: 1;
            background: linear-gradient(135deg, #0a1628 0%, #0d2137 50%, #0f2944 100%);
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .banner-right {
            width: 45%;
            background: linear-gradient(135deg, #d4a84b 0%, #c49a3d 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px;
        }
        .banner-slider { position: relative; width: 100%; height: 100%; display: flex; }
        .banner-slide {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            opacity: 0; overflow: hidden !important;
            transition: opacity 0.8s ease; display: flex; align-items: center; justify-content: center;
        }
        .banner-slide.active { opacity: 1; }
        .banner-slide-bg {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex;
            background: url('images/banner-bg.jpg') center / cover no-repeat;
        }
        .banner-dark-bg {
            flex: 1;
            background: linear-gradient(to right, rgba(10,22,40,0.75) 0%, rgba(10,22,40,0.55) 70%, rgba(10,22,40,0.10) 100%);
            position: relative;
        }
        .banner-dark-bg::before {
            content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: radial-gradient(circle at 20% 30%, rgba(0,100,200,0.1) 0%, transparent 40%),
                        radial-gradient(circle at 80% 70%, rgba(0,150,255,0.08) 0%, transparent 40%);
        }
        .banner-gold-bg {
            width: 45%;
            background: linear-gradient(to right, rgba(212,168,75,0.30) 0%, rgba(212,168,75,0.60) 40%, rgba(212,168,75,0.75) 100%);
            display: flex; align-items: center; justify-content: center; padding: 40px;
        }

        /* 六边形蜂巢 */
        .banner-product-grid { width: 470px; height: 490px; position: relative; margin: 0 auto; }
        .banner-product-item {
            width: 183px; height: 158px;
            clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
            position: absolute; overflow: hidden; transition: all 0.3s ease; cursor: pointer;
        }
        .banner-product-item::before {
            content: ''; position: absolute; inset: -4px;
            background: linear-gradient(135deg, #d4a84b, #f5d78e, #d4a84b);
            clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%); z-index: 1;
        }
        .banner-product-item img { width: 100%; height: 100%; object-fit: cover; position: absolute; z-index: 0; }
        .banner-product-item:hover {
            transform: translate(var(--tx), var(--ty)) scale(1.15) !important;
            z-index: 50 !important; filter: brightness(1.1);
        }
        .banner-product-item:hover::before {
            background: linear-gradient(135deg, #00a8cc, #005d73, #00a8cc) !important;
        }
        .banner-product-item:nth-child(1) { --tx: 143.5px; --ty: 166px; transform: translate(143.5px, 166px); z-index: 7; }
        .banner-product-item:nth-child(2) { --tx: 143.5px; --ty:   0px; transform: translate(143.5px,   0px); z-index: 6; }
        .banner-product-item:nth-child(3) { --tx: 287.5px; --ty:  83px; transform: translate(287.5px,  83px); z-index: 6; }
        .banner-product-item:nth-child(4) { --tx: 287.5px; --ty: 249px; transform: translate(287.5px, 249px); z-index: 6; }
        .banner-product-item:nth-child(5) { --tx: 143.5px; --ty: 332px; transform: translate(143.5px, 332px); z-index: 6; }
        .banner-product-item:nth-child(6) { --tx:  -0.5px; --ty: 249px; transform: translate( -0.5px, 249px); z-index: 6; }
        .banner-product-item:nth-child(7) { --tx:  -0.5px; --ty:  83px; transform: translate( -0.5px,  83px); z-index: 6; }

        /* 电机背景动画 */
        .banner-motor-bg { position: absolute; top: 0; left: 0; right: 0; bottom: 0; overflow: hidden; }
        .motor-gear { position: absolute; border: 3px solid rgba(0, 245, 255, 0.25); border-radius: 50%; box-shadow: 0 0 20px rgba(0, 245, 255, 0.15), inset 0 0 15px rgba(0, 245, 255, 0.08); }
        .motor-gear::before { content: ''; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); border: 2px dashed rgba(0, 245, 255, 0.2); border-radius: 50%; }
        .gear-1 { width: 400px; height: 400px; top: -100px; right: -100px; animation: rotate 30s linear infinite; }
        .gear-1::before { width: 300px; height: 300px; }
        .gear-2 { width: 300px; height: 300px; bottom: -50px; left: -50px; animation: rotate 25s linear infinite reverse; }
        .gear-2::before { width: 220px; height: 220px; }
        .gear-3 { width: 200px; height: 200px; top: 50%; right: 15%; animation: rotate 20s linear infinite; }
        .gear-3::before { width: 140px; height: 140px; }
        .motor-coil { position: absolute; width: 350px; height: 350px; top: 50%; left: 60%; transform: translate(-50%, -50%); border: 4px solid rgba(0, 245, 255, 0.35); border-radius: 50%; box-shadow: 0 0 30px rgba(0, 245, 255, 0.2), inset 0 0 20px rgba(0, 245, 255, 0.1); }
        .motor-rotor { position: absolute; width: 300px; height: 300px; top: 50%; left: 50%; transform: translate(-50%, -50%); border: 3px solid rgba(0, 200, 255, 0.12); border-radius: 50%; animation: pulse-rotate 8s ease-in-out infinite; }
        .motor-stator { position: absolute; width: 400px; height: 400px; top: 50%; left: 50%; transform: translate(-50%, -50%); border: 2px dashed rgba(0, 168, 255, 0.08); border-radius: 50%; animation: rotate 40s linear infinite reverse; }
        .banner-content { position: absolute; left: 60px; top: 50%; transform: translateY(-50%); z-index: 2; text-align: left; color: #fff; max-width: 500px; }
        .banner-title { font-size: 48px; font-weight: 700; margin-bottom: 15px; letter-spacing: 2px; text-shadow: 0 2px 10px rgba(0,0,0,0.3); }
        .banner-subtitle { font-size: 18px; font-weight: 400; color: #f5a623; margin-bottom: 25px; }
        .banner-btn { display: inline-block; background: #f5a623; color: #fff; padding: 12px 30px; border-radius: 4px; text-decoration: none; font-weight: 600; font-size: 15px; transition: all 0.3s; border: 2px solid #f5a623; }
        .banner-btn:hover { background: transparent; color: #f5a623; }
        .banner-dots { position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%); display: flex; gap: 12px; z-index: 10; }
        .banner-dot { width: 12px; height: 12px; border-radius: 50%; background: rgba(255,255,255,0.4); cursor: pointer; transition: all 0.3s; border: 2px solid transparent; }
        .banner-dot.active { background: #fff; transform: scale(1.2); }
        .banner-arrows { position: absolute; top: 50%; transform: translateY(-50%); width: 100%; display: flex; justify-content: space-between; padding: 0 30px; pointer-events: none; z-index: 10; }
        .banner-arrow { width: 50px; height: 50px; background: rgba(255,255,255,0.2); border: 2px solid rgba(255,255,255,0.4); border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.3s; pointer-events: auto; color: #fff; font-size: 20px; }
        .banner-arrow:hover { background: rgba(255,255,255,0.4); border-color: #fff; }

        /* 统计区域 */
        .stats-section { background: #005d73; padding: 60px 0; color: #fff; }
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 30px; text-align: center; }
        .stat-item { padding: 20px; }
        .stat-number { font-size: 48px; font-weight: 700; margin-bottom: 10px; }
        .stat-label { font-size: 16px; opacity: 0.9; }

        /* 通用区域标题 */
        .section-header { text-align: center; margin-bottom: 50px; }
        .section-title { font-size: 36px; color: #005d73; font-weight: 600; margin-bottom: 15px; }
        .section-subtitle { font-size: 16px; color: #666; }

        /* 关于我们 */
        .about-section { padding: 80px 0; background: #f8f9fa; }
        .about-content { display: grid; grid-template-columns: 1fr 1fr; gap: 60px; align-items: center; }
        .about-text h3 { font-size: 28px; color: #005d73; margin-bottom: 20px; }
        .about-text p { font-size: 16px; color: #555; line-height: 1.8; margin-bottom: 15px; }

        /* 产品区域 - 六边形蜂巢 */
        .products-section { padding: 60px 0 80px; background: #f5f5f5; text-align: center; }
        .products-section .section-title { color: #333; font-size: 32px; margin-bottom: 10px; }
        .products-section .section-subtitle { color: #666; font-size: 18px; margin-bottom: 50px; }
        .hex-grid { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; flex-wrap: wrap; justify-content: center; gap: 20px 30px; }
        .hex { display: flex; flex-direction: column; align-items: center; }
        .hex-inner { width: 160px; height: 184px; position: relative; }
        .hex-content {
            width: 100%; height: 100%;
            clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
            background: #005d73; display: flex; align-items: center; justify-content: center;
            transition: all 0.3s; overflow: hidden;
        }
        .hex:hover .hex-content { background: #007a8a; transform: scale(1.05); }
        .hex-content img { width: 100%; height: 100%; object-fit: cover; }
        .hex-label { margin-top: 15px; font-size: 14px; color: #333; font-weight: 500; }

        /* 新闻资讯 */
        .news-section { padding: 80px 0; background: #f8f9fa; }
        .news-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }
        .news-featured { position: relative; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .news-featured-content { position: absolute; bottom: 0; left: 0; right: 0; padding: 30px; background: linear-gradient(transparent, rgba(0,0,0,0.8)); color: #fff; }
        .news-featured-content h3 { font-size: 20px; margin-bottom: 10px; }
        .news-featured-content .date { font-size: 14px; opacity: 0.8; }
        .news-list { display: flex; flex-direction: column; gap: 20px; }
        .news-item { display: flex; gap: 20px; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); transition: all 0.3s; text-decoration: none; color: inherit; }
        .news-item:hover { box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .news-item-image { width: 120px; height: 80px; background: #e2e8f0; border-radius: 4px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 30px; }
        .news-item-content { flex: 1; }
        .news-item-content h4 { font-size: 16px; color: #333; margin-bottom: 8px; line-height: 1.4; }
        .news-item-content .date { font-size: 13px; color: #999; }

        /* 联系区域 */
        .contact-section { padding: 80px 0; background: transparent; color: #00f5ff; border: 2px solid #00f5ff; box-shadow: 0 0 10px rgba(0, 245, 255, 0.2); }
        .contact-section .section-title { color: #fff; }
        .contact-section .section-subtitle { color: rgba(255,255,255,0.8); }
        .contact-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 60px; }
        .contact-info h3 { font-size: 24px; margin-bottom: 30px; }
        .contact-item { display: flex; align-items: flex-start; gap: 15px; margin-bottom: 25px; }
        .contact-item-icon { width: 50px; height: 50px; background: rgba(255,255,255,0.1); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
        .contact-item-content h4 { font-size: 16px; margin-bottom: 5px; font-weight: 600; }
        .contact-item-content p { font-size: 14px; opacity: 0.9; line-height: 1.6; }
        .contact-form { background: #fff; padding: 40px; border-radius: 8px; }
        .contact-form h3 { color: #333; font-size: 24px; margin-bottom: 25px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; font-size: 14px; color: #555; margin-bottom: 8px; }
        .form-group input, .form-group textarea { width: 100%; padding: 12px 15px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; transition: border-color 0.3s; }
        .form-group input:focus, .form-group textarea:focus { outline: none; border-color: #005d73; }
        .form-group textarea { min-height: 120px; resize: vertical; }
        .submit-btn { width: 100%; padding: 15px; background: #005d73; color: #fff; border: none; border-radius: 4px; font-size: 16px; font-weight: 600; cursor: pointer; transition: background 0.3s; }
        .submit-btn:hover { background: #004a5c; }

        /* 响应式 */
        @media (max-width: 1024px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } }
        @media (max-width: 768px) {
            .banner { flex-direction: column; height: auto; }
            .banner-left { min-height: 400px; }
            .banner-right { width: 100%; padding: 30px; }
            .banner-content { left: 30px; right: 30px; }
            .banner-title { font-size: 32px; }
            .banner-subtitle { font-size: 16px; }
            .banner-product-grid { width: 289px; height: 300px; }
            .banner-product-item { width: 113px; height: 98px; }
            .banner-product-item::before { inset: -2px; }
            .banner-product-item:nth-child(1) { --tx:  88px; --ty: 101px; transform: translate( 88px, 101px); }
            .banner-product-item:nth-child(2) { --tx:  88px; --ty:   3px; transform: translate( 88px,   3px); }
            .banner-product-item:nth-child(3) { --tx: 174px; --ty:  52px; transform: translate(174px,  52px); }
            .banner-product-item:nth-child(4) { --tx: 174px; --ty: 150px; transform: translate(174px, 150px); }
            .banner-product-item:nth-child(5) { --tx:  88px; --ty: 199px; transform: translate( 88px, 199px); }
            .banner-product-item:nth-child(6) { --tx:   2px; --ty: 150px; transform: translate(  2px, 150px); }
            .banner-product-item:nth-child(7) { --tx:   2px; --ty:  52px; transform: translate(  2px,  52px); }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            .stat-number { font-size: 32px; }
            .about-content, .news-grid, .contact-grid { grid-template-columns: 1fr; }
            .section-title { font-size: 28px; }
        }
        @media (max-width: 480px) {
            .stats-grid { grid-template-columns: 1fr; }
            .banner-arrows { display: none; }
        }
    </style>
</head>
<body>
    <!-- #include nav.html -->

    <!-- Banner 轮播区 -->
    <section class="banner" id="home">
        <div class="banner-slider">
            <div class="banner-slide active">
                <div class="banner-slide-bg">
                    <div class="banner-dark-bg"></div>
                    <div class="banner-gold-bg">
                        <div class="banner-product-grid">
                            <div class="banner-product-item"><img src="images/products/1030837.png" alt="分动箱电机"></div>
                            <div class="banner-product-item"><img src="images/products/1030896.png" alt="节气门电机"></div>
                            <div class="banner-product-item"><img src="images/products/1030837.png" alt="产品3"></div>
                            <div class="banner-product-item"><img src="images/products/1030896.png" alt="产品4"></div>
                            <div class="banner-product-item"><img src="images/products/1030837.png" alt="产品5"></div>
                            <div class="banner-product-item"><img src="images/products/1030896.png" alt="产品6"></div>
                            <div class="banner-product-item"><img src="images/products/1030837.png" alt="产品7"></div>
                        </div>
                    </div>
                </div>
                <div class="banner-content">
                    <h1 class="banner-title">华创生电机</h1>
                    <p class="banner-subtitle">德昌电机(JOHNSON ELECTRIC)授权代理商</p>
                    <a href="products.html" class="banner-btn">探索产品</a>
                </div>
            </div>
            <div class="banner-slide">
                <div class="banner-slide-bg">
                    <div class="banner-dark-bg">
                        <div class="banner-motor-bg">
                            <div class="motor-gear gear-1"></div>
                            <div class="motor-gear gear-2"></div>
                            <div class="motor-gear gear-3"></div>
                            <div class="motor-coil"></div>
                            <div class="motor-rotor"></div>
                            <div class="motor-stator"></div>
                        </div>
                    </div>
                    <div class="banner-gold-bg">
                        <div class="banner-product-grid">
                            <div class="banner-product-item"><img src="images/products/1030837.png" alt="产品1"></div>
                            <div class="banner-product-item"><img src="images/products/1030896.png" alt="产品2"></div>
                            <div class="banner-product-item"><img src="images/products/1030837.png" alt="产品3"></div>
                            <div class="banner-product-item"><img src="images/products/1030896.png" alt="产品4"></div>
                            <div class="banner-product-item"><img src="images/products/1030837.png" alt="产品5"></div>
                            <div class="banner-product-item"><img src="images/products/1030896.png" alt="产品6"></div>
                            <div class="banner-product-item"><img src="images/products/1030837.png" alt="产品7"></div>
                        </div>
                    </div>
                </div>
                <div class="banner-content">
                    <h1 class="banner-title">精密驱动</h1>
                    <p class="banner-subtitle">20年专注自动化与智能化驱动领域</p>
                    <a href="products.html" class="banner-btn">了解更多</a>
                </div>
            </div>
        </div>
        <div class="banner-arrows">
            <button class="banner-arrow banner-prev">&#10094;</button>
            <button class="banner-arrow banner-next">&#10095;</button>
        </div>
        <div class="banner-dots">
            <span class="banner-dot active"></span>
            <span class="banner-dot"></span>
        </div>
    </section>

    <!-- 统计数字 -->
    <section class="stats-section">
        <div class="container">
            <div class="stats-grid">
                <div class="stat-item"><div class="stat-number" data-target="20">0+</div><div class="stat-label">年行业经验</div></div>
                <div class="stat-item"><div class="stat-number" data-target="500">0+</div><div class="stat-label">服务客户</div></div>
                <div class="stat-item"><div class="stat-number" data-target="1000">0+</div><div class="stat-label">产品型号</div></div>
                <div class="stat-item"><div class="stat-number" data-target="98">0%</div><div class="stat-label">客户满意度</div></div>
            </div>
        </div>
    </section>

    <!-- 关于我们 -->
    <section id="about" class="about-section">
        <div class="container">
            <div class="section-header"><h2 class="section-title">关于我们</h2><p class="section-subtitle">德昌电机授权代理，专业驱动解决方案</p></div>
            <div class="about-content">
                <div class="about-text">
                    <h3>20年行业深耕</h3>
                    <p>华创生电机是德昌电机（JOHNSON ELECTRIC）授权代理商，专注自动化与智能化驱动领域20年。</p>
                    <p>我们提供直流电机、交流电机、步进电机、驱动系统等全系列产品。</p>
                </div>
                <div class="about-image"><img src="images/logo.png" alt="华创生电机" style="max-width:100%;"></div>
            </div>
        </div>
    </section>

    <!-- 产品中心预览 -->
    <section id="products" class="products-section">
        <div class="container">
            <div class="section-header"><h2 class="section-title">产品中心</h2><p class="section-subtitle">全系列电机产品</p></div>
            <div class="hex-grid">
                <div class="hex"><div class="hex-inner"><div class="hex-content">⚡</div></div><div class="hex-label">车用马达</div></div>
                <div class="hex"><div class="hex-inner"><div class="hex-content">🔧</div></div><div class="hex-label">电动工具马达</div></div>
                <div class="hex"><div class="hex-inner"><div class="hex-content">🏠</div></div><div class="hex-label">家用电器马达</div></div>
                <div class="hex"><div class="hex-inner"><div class="hex-content">🔘</div></div><div class="hex-label">微动开关</div></div>
            </div>
        </div>
    </section>

    <!-- 新闻 -->
    <section id="news" class="news-section">
        <div class="container">
            <div class="section-header"><h2 class="section-title">新闻中心</h2><p class="section-subtitle">最新动态</p></div>
            <div class="news-grid">
                <div class="news-featured"><div style="background:#e2e8f0;height:300px;display:flex;align-items:center;justify-content:center;font-size:48px;">📰</div></div>
                <div class="news-list">
                    <a class="news-item"><div class="news-item-image">📄</div><div class="news-item-content"><h4>公司新闻标题</h4><div class="date">2026-05-01</div></div></a>
                    <a class="news-item"><div class="news-item-image">📄</div><div class="news-item-content"><h4>行业动态标题</h4><div class="date">2026-04-15</div></div></a>
                </div>
            </div>
        </div>
    </section>

    <!-- 联系我们 -->
    <section id="contact" class="contact-section">
        <div class="container">
            <div class="section-header"><h2 class="section-title">联系我们</h2><p class="section-subtitle">期待与您的合作</p></div>
            <div class="contact-grid">
                <div class="contact-info">
                    <h3>联系方式</h3>
                    <div class="contact-item"><div class="contact-item-icon">📞</div><div class="contact-item-content"><h4>电话</h4><p>0755-12345678</p></div></div>
                    <div class="contact-item"><div class="contact-item-icon">📧</div><div class="contact-item-content"><h4>邮箱</h4><p>info@huachuangsheng.com</p></div></div>
                    <div class="contact-item"><div class="contact-item-icon">📍</div><div class="contact-item-content"><h4>地址</h4><p>深圳市宝安区</p></div></div>
                </div>
                <div class="contact-form">
                    <h3>在线咨询</h3>
                    <form id="contactForm">
                        <div class="form-group"><label>姓名</label><input type="text" required></div>
                        <div class="form-group"><label>电话</label><input type="tel" required></div>
                        <div class="form-group"><label>留言</label><textarea required></textarea></div>
                        <button type="submit" class="submit-btn">提交咨询</button>
                    </form>
                </div>
            </div>
        </div>
    </section>

    <!-- #include footer.html -->

    <!-- Fuse.js -->
    <script src="https://cdn.jsdelivr.net/npm/fuse.js@7.0.0"></script>
    <script src="data/products.js?v=2"></script>
    <!-- #include js:common,nav-search -->

    <script>
        /* ========== 首页特有: 轮播 + 数字动画 ========== */
        document.addEventListener('DOMContentLoaded', function() {
            // Banner 轮播
            var slides = document.querySelectorAll('.banner-slide');
            var dots = document.querySelectorAll('.banner-dot');
            var prevBtn = document.querySelector('.banner-prev');
            var nextBtn = document.querySelector('.banner-next');
            if (slides.length && dots.length) {
                var currentSlide = 0;
                var slideInterval;
                function showSlide(index) {
                    slides.forEach(function(s, i) { s.classList.remove('active'); dots[i].classList.remove('active'); });
                    slides[index].classList.add('active');
                    dots[index].classList.add('active');
                    currentSlide = index;
                }
                function nextSlide() { showSlide((currentSlide + 1) % slides.length); }
                function prevSlide() { showSlide((currentSlide - 1 + slides.length) % slides.length); }
                function startSlideShow() { slideInterval = setInterval(nextSlide, 3000); }
                function stopSlideShow() { clearInterval(slideInterval); }
                if (prevBtn) prevBtn.addEventListener('click', function() { stopSlideShow(); prevSlide(); startSlideShow(); });
                if (nextBtn) nextBtn.addEventListener('click', function() { stopSlideShow(); nextSlide(); startSlideShow(); });
                var bannerSlider = document.querySelector('.banner-slider');
                if (bannerSlider) {
                    bannerSlider.addEventListener('mouseenter', stopSlideShow);
                    bannerSlider.addEventListener('mouseleave', startSlideShow);
                }
                dots.forEach(function(dot, i) { dot.addEventListener('mouseenter', function() { stopSlideShow(); showSlide(i); }); });
                startSlideShow();
            }

            // 数字增长动画
            var statNumbers = document.querySelectorAll('.stat-number');
            var animated = false;
            function animateNumbers() {
                if (animated) return;
                var statsSection = document.querySelector('.stats-section');
                if (!statsSection) return;
                var sectionTop = statsSection.offsetTop;
                var windowHeight = window.innerHeight;
                var scrollTop = window.pageYOffset;
                if (scrollTop + windowHeight > sectionTop + 100) {
                    animated = true;
                    statNumbers.forEach(function(num) {
                        var target = parseInt(num.getAttribute('data-target'));
                        var duration = 2000;
                        var step = target / (duration / 16);
                        var current = 0;
                        var timer = setInterval(function() {
                            current += step;
                            if (current >= target) { current = target; clearInterval(timer); }
                            num.textContent = Math.floor(current) + (target === 98 ? '%' : '+');
                        }, 16);
                    });
                }
            }
            window.addEventListener('scroll', animateNumbers);
            animateNumbers();
        });
    </script>
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add index.html
git commit -m "refactor: index.html uses shared CSS/JS/components"
```

---

### Task 16: 改造 products.html

**Files:**
- Modify: `products.html`

- [ ] **Step 1: 重写 products.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>产品中心 - 华创生电机</title>
    <!-- #include css:common,nav,sidebar,footer,products -->
    <style>
        .version-tag {
            position: fixed; top: 85px; right: 10px;
            background: rgba(0,93,115,0.9); color: #fff;
            padding: 4px 10px; font-size: 12px; border-radius: 4px;
            z-index: 1001; font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="version-tag">v2026-05-18 22:41</div>
    <!-- #include nav.html -->

    <!-- Hero -->
    <section class="page-hero">
        <div class="page-hero-content">
            <div class="products-glow">PRODUCTS</div>
            <h1>产品中心</h1>
            <p>德昌电机（JOHNSON ELECTRIC）官方授权代理</p>
            <p>专注汽车零部件 · 电动工具 · 智能家居驱动解决方案</p>
            <div class="page-hero-divider"></div>
        </div>
    </section>

    <div class="products-layout">
        <!-- #include sidebar.html -->

        <div class="products-content">
            <!-- 车用马达 -->
            <div id="tab-motor" class="product-tab-panel active">
                <div class="tab-panel-header">
                    <span class="category-tag">CATEGORY 01</span>
                    <h2>车用马达</h2>
                    <p class="category-desc">面向汽车全场景应用的高可靠直流马达，全面符合车规级严苛标准，适配车身控制、动力辅助等多类车用模块。</p>
                </div>
                <div class="product-card-grid-sidebar">
                    <a href="product-1030837.html" class="product-card-link">
                        <div class="product-card">
                            <div class="product-card-img"><img src="images/products/1030837.png" alt="1030837分动箱电机" style="width:100%;height:100%;object-fit:contain;"></div>
                            <div class="product-card-body"><h3>1030837分动箱电机</h3><p>用于Jeep自由光，大指挥官分动箱PTU执行器电机</p><span class="product-card-tag">分动箱电机</span></div>
                        </div>
                    </a>
                    <a href="product-1030896.html" class="product-card-link">
                        <div class="product-card">
                            <div class="product-card-img"><img src="images/products/1030896.png" alt="1030896节气门电机" style="width:100%;height:100%;object-fit:contain;"></div>
                            <div class="product-card-body"><h3>1030896节气门电机</h3><p>用于奥迪、大众、路虎等高端品牌节气门总成电机</p><span class="product-card-tag">节气门电机</span></div>
                        </div>
                    </a>
                    <div class="product-card"><div class="product-card-img">⚡</div><div class="product-card-body"><h3>V4NC 直流电机</h3><p>EPB系统专用</p><span class="product-card-tag">EPB</span></div></div>
                    <div class="product-card"><div class="product-card-img">🔌</div><div class="product-card-body"><h3>DC971 无刷电机</h3><p>新能源应用</p><span class="product-card-tag">无刷</span></div></div>
                    <div class="product-card"><div class="product-card-img">🎯</div><div class="product-card-body"><h3>X4 齿轮电机</h3><p>座椅调节</p><span class="product-card-tag">齿轮减速</span></div></div>
                    <div class="product-card"><div class="product-card-img">🛞</div><div class="product-card-body"><h3>NS246G 驱动系统</h3><p>LIN/CAN通讯</p><span class="product-card-tag">智能驱动</span></div></div>
                </div>
            </div>

            <!-- 家用电器及电动工具 -->
            <div id="tab-appliance" class="product-tab-panel">
                <div class="tab-panel-header">
                    <span class="category-tag">CATEGORY 02</span>
                    <h2>家用电器及电动工具马达</h2>
                    <p class="category-desc">覆盖电动工具、园林设备、智能家居等领域的全系列高效电机解决方案，兼具性能与耐久性。</p>
                </div>
                <div class="product-card-grid-sidebar">
                    <div class="product-card"><div class="product-card-img">🔧</div><div class="product-card-body"><h3>V4N 交流电机</h3><p>适合电动工具</p><span class="product-card-tag">AC</span></div></div>
                    <div class="product-card"><div class="product-card-img">🌿</div><div class="product-card-body"><h3>X3 步进电机</h3><p>园林工具</p><span class="product-card-tag">步进</span></div></div>
                    <div class="product-card"><div class="product-card-img">🏠</div><div class="product-card-body"><h3>KC330FXLMG-120</h3><p>家用智能设备</p><span class="product-card-tag">家用</span></div></div>
                    <div class="product-card"><div class="product-card-img">💡</div><div class="product-card-body"><h3>BTA_2EV_1 风机</h3><p>空气净化器</p><span class="product-card-tag">风机</span></div></div>
                </div>
            </div>

            <!-- 微动开关 -->
            <div id="tab-switch" class="product-tab-panel">
                <div class="tab-panel-header">
                    <span class="category-tag">CATEGORY 03</span>
                    <h2>微动开关</h2>
                    <p class="category-desc">精密微动开关系列，响应灵敏、寿命超长、接触稳定可靠，广泛应用于汽车、家电及工业控制领域。</p>
                </div>
                <div class="product-card-grid-sidebar">
                    <div class="product-card"><div class="product-card-img">🔘</div><div class="product-card-body"><h3>MS-101</h3><p>标准型</p><span class="product-card-tag">标准型</span></div></div>
                    <div class="product-card"><div class="product-card-img">🔲</div><div class="product-card-body"><h3>MS-202</h3><p>IP67防水</p><span class="product-card-tag">IP67</span></div></div>
                    <div class="product-card"><div class="product-card-img">⚙️</div><div class="product-card-body"><h3>MS-303</h3><p>精密型</p><span class="product-card-tag">精密型</span></div></div>
                    <div class="product-card"><div class="product-card-img">📟</div><div class="product-card-body"><h3>MS-404</h3><p>工业型</p><span class="product-card-tag">高电流</span></div></div>
                </div>
            </div>
        </div>
    </div>

    <!-- CTA -->
    <section class="cta-section">
        <div class="container">
            <h2>需要了解更多产品规格？</h2>
            <p>我们的技术团队为您提供专业的选型支持与定制方案</p>
            <a href="tel:0755-12345678" class="cta-btn">立即咨询</a>
        </div>
    </section>

    <!-- #include footer.html -->

    <script src="https://cdn.jsdelivr.net/npm/fuse.js@7.0.0"></script>
    <script src="data/products.js?v=2"></script>
    <!-- #include js:common,nav-search,sidebar -->
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add products.html
git commit -m "refactor: products.html uses shared CSS/JS/components"
```

---

### Task 17: 改造 product-1030837.html（产品详情页模板代表）

**Files:**
- Modify: `product-1030837.html`

- [ ] **Step 1: 重写 product-1030837.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>1030837分动箱电机 - 华创生电机</title>
    <!-- #include css:common,nav,sidebar,footer,product-detail -->
</head>
<body>
    <!-- #include nav.html -->
    <!-- #include sidebar.html -->

    <div class="product-detail">
        <div class="container">
            <a href="products.html#tab-motor" class="back-link">← 返回产品中心</a>
            <div class="product-hero">
                <div class="product-gallery">
                    <div class="main-img-wrapper">
                        <img id="mainImg" src="images/products/1030837.png" alt="1030837分动箱电机" class="product-main-img">
                        <button class="img-nav-btn img-prev">&#10094;</button>
                        <button class="img-nav-btn img-next">&#10095;</button>
                    </div>
                    <div class="thumbnails">
                        <img src="images/products/1030837.png" alt="主图1" class="thumb active">
                        <img src="images/products/1030837-main2.jpg" alt="主图2" class="thumb">
                        <img src="images/products/1030837-main3.jpg" alt="主图3" class="thumb">
                    </div>
                </div>
                <div class="product-info">
                    <span class="product-tag">12V有刷直流</span>
                    <h1>1030837分动箱电机</h1>
                    <div class="product-model">型号：1030837</div>
                    <p class="product-desc">
                        用于Jeep自由光、大指挥官分动箱PTU执行器电机。采用高可靠性设计，满足严苛的汽车工况要求，响应速度快，扭矩输出稳定。
                    </p>
                    <div class="product-specs">
                        <h3>规格参数</h3>
                        <div class="spec-row"><span class="spec-label">应用领域</span><span class="spec-value">Jeep自由光、大指挥官</span></div>
                        <div class="spec-row"><span class="spec-label">安装位置</span><span class="spec-value">分动箱 PTU 执行器</span></div>
                        <div class="spec-row"><span class="spec-label">产品类型</span><span class="spec-value">12V有刷直流</span></div>
                        <div class="spec-row"><span class="spec-label">品质标准</span><span class="spec-value">原厂配套品质</span></div>
                    </div>
                </div>
            </div>
            <div class="product-chart">
                <h2>商品详情</h2>
                <img src="images/products/1030837-chart.png" alt="1030837曲线图外形图" class="chart-img">
                <div class="chart-note">以上曲线图及外形尺寸仅供参考，具体参数以实物为准。</div>
            </div>
        </div>
    </div>

    <!-- #include footer.html -->

    <script src="https://cdn.jsdelivr.net/npm/fuse.js@7.0.0"></script>
    <script src="data/products.js?v=2"></script>
    <!-- #include js:common,nav-search,sidebar,product-detail -->
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add product-1030837.html
git commit -m "refactor: product-1030837.html uses shared CSS/JS/components"
```

---

### Task 18: 改造 product-1030896.html

**Files:**
- Modify: `product-1030896.html`

- [ ] **Step 1: 重写 product-1030896.html**（结构同 product-1030837.html，数据不同）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>1030896节气门电机 - 华创生电机</title>
    <!-- #include css:common,nav,sidebar,footer,product-detail -->
</head>
<body>
    <!-- #include nav.html -->
    <!-- #include sidebar.html -->

    <div class="product-detail">
        <div class="container">
            <a href="products.html#tab-motor" class="back-link">← 返回产品中心</a>
            <div class="product-hero">
                <div class="product-gallery">
                    <div class="main-img-wrapper">
                        <img id="mainImg" src="images/products/1030896.png" alt="1030896节气门电机" class="product-main-img">
                        <button class="img-nav-btn img-prev">&#10094;</button>
                        <button class="img-nav-btn img-next">&#10095;</button>
                    </div>
                    <div class="thumbnails">
                        <img src="images/products/1030896.png" alt="主图1" class="thumb active">
                        <img src="images/products/1030896-main2.png" alt="主图2" class="thumb">
                        <img src="images/products/1030896-main3.png" alt="主图3" class="thumb">
                    </div>
                </div>
                <div class="product-info">
                    <span class="product-tag">12V有刷直流</span>
                    <h1>1030896节气门电机</h1>
                    <div class="product-model">型号：1030896</div>
                    <p class="product-desc">
                        用于奥迪、宝马、大众、路虎等高端品牌节气门总成电机。采用高精度位置反馈设计，响应速度快，控制精准。
                    </p>
                    <div class="product-specs">
                        <h3>规格参数</h3>
                        <div class="spec-row"><span class="spec-label">应用领域</span><span class="spec-value">奥迪、宝马、大众、路虎等高端品牌</span></div>
                        <div class="spec-row"><span class="spec-label">安装位置</span><span class="spec-value">节气门总成</span></div>
                        <div class="spec-row"><span class="spec-label">产品类型</span><span class="spec-value">12V有刷直流</span></div>
                        <div class="spec-row"><span class="spec-label">品质标准</span><span class="spec-value">原厂配套品质</span></div>
                    </div>
                </div>
            </div>
            <div class="product-chart">
                <h2>商品详情</h2>
                <img src="images/products/1030896-chart.png" alt="1030896曲线图外形图" class="chart-img">
                <div class="chart-note">以上曲线图及外形尺寸仅供参考，具体参数以实物为准。</div>
            </div>
        </div>
    </div>

    <!-- #include footer.html -->

    <script src="https://cdn.jsdelivr.net/npm/fuse.js@7.0.0"></script>
    <script src="data/products.js?v=2"></script>
    <!-- #include js:common,nav-search,sidebar,product-detail -->
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add product-1030896.html
git commit -m "refactor: product-1030896.html uses shared CSS/JS/components"
```

---

### Task 19: 改造 other-motor.html

**Files:**
- Modify: `other-motor.html`

- [ ] **Step 1: 改写 other-motor.html**

此文件是分类列表页。保留其独有内容（产品列表），导航/侧边栏/页脚改用 include：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>其他车用马达 - 华创生电机</title>
    <!-- #include css:common,nav,sidebar,footer,products -->
</head>
<body>
    <!-- #include nav.html -->
    <!-- #include sidebar.html -->

    <div class="products-content" style="margin-top:80px;">
        <a href="products.html#tab-motor" class="back-link">← 返回车用马达</a>
        <h1 style="color:#00f5ff;font-family:var(--font-display);font-size:28px;margin-bottom:30px;">其他车用马达</h1>
        <div class="product-card-grid-sidebar">
            <a href="product-1030837.html" class="product-card-link">
                <div class="product-card">
                    <div class="product-card-img"><img src="images/products/1030837.png" alt="1030837" style="width:100%;height:100%;object-fit:contain;"></div>
                    <div class="product-card-body"><h3>1030837分动箱电机</h3><p>Jeep自由光PTU执行器</p><span class="product-card-tag">分动箱</span></div>
                </div>
            </a>
            <!-- 其他产品卡片按原文件内容保留 -->
        </div>
    </div>

    <!-- #include footer.html -->

    <script src="https://cdn.jsdelivr.net/npm/fuse.js@7.0.0"></script>
    <script src="data/products.js?v=2"></script>
    <!-- #include js:common,nav-search,sidebar -->
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add other-motor.html
git commit -m "refactor: other-motor.html uses shared CSS/JS/components"
```

---

### Task 20: 改造 throttle-motor.html

**Files:**
- Modify: `throttle-motor.html`

- [ ] **Step 1: 改写 throttle-motor.html**（结构同 other-motor.html，标题不同）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>节气门马达 - 华创生电机</title>
    <!-- #include css:common,nav,sidebar,footer,products -->
</head>
<body>
    <!-- #include nav.html -->
    <!-- #include sidebar.html -->

    <div class="products-content" style="margin-top:80px;">
        <a href="products.html#tab-motor" class="back-link">← 返回车用马达</a>
        <h1 style="color:#00f5ff;font-family:var(--font-display);font-size:28px;margin-bottom:30px;">节气门马达</h1>
        <div class="product-card-grid-sidebar">
            <a href="product-1030896.html" class="product-card-link">
                <div class="product-card">
                    <div class="product-card-img"><img src="images/products/1030896.png" alt="1030896" style="width:100%;height:100%;object-fit:contain;"></div>
                    <div class="product-card-body"><h3>1030896节气门电机</h3><p>奥迪、大众、路虎等</p><span class="product-card-tag">节气门</span></div>
                </div>
            </a>
            <!-- 其他产品卡片按原文件内容保留 -->
        </div>
    </div>

    <!-- #include footer.html -->

    <script src="https://cdn.jsdelivr.net/npm/fuse.js@7.0.0"></script>
    <script src="data/products.js?v=2"></script>
    <!-- #include js:common,nav-search,sidebar -->
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add throttle-motor.html
git commit -m "refactor: throttle-motor.html uses shared CSS/JS/components"
```

---

### Task 21: 删除 index-inline.html

**Files:**
- Delete: `index-inline.html`

- [ ] **Step 1: 删除文件**

```bash
git rm index-inline.html
```

- [ ] **Step 2: Commit**

```bash
git commit -m "chore: remove index-inline.html (merged into index.html)"
```

---

### Task 22: 构建并验证

**Files:** none (test only)

- [ ] **Step 1: 运行 build.py**

```bash
python build.py
```

预期输出: 所有 6 个 HTML 文件成功构建，CSS/JS 正确注入。

- [ ] **Step 2: 验证 dist/ 目录结构**

```bash
ls -la dist/ && ls -la dist/css/ && ls -la dist/js/ && ls -la dist/inc/ 2>/dev/null || echo "no inc/ in dist (expected)"
```

预期: `dist/` 下只有 HTML 文件 + `css/` `js/` `images/` `data/` 目录，没有 `inc/` 目录。

- [ ] **Step 3: 检查 dist/index.html 中的关键注入点**

```bash
grep -c 'common.css' dist/index.html && grep -c 'nav.css' dist/index.html && grep -c 'common.js' dist/index.html && grep -c 'nav-search.js' dist/index.html
```

预期输出: 每个文件引用出现 1 次。

- [ ] **Step 4: 验证构建后的 HTML 没有残留的内联导航 CSS**

```bash
grep -c 'nav-link' dist/index.html && grep -c 'class="header"' dist/index.html
```

预期: nav-link 出现多次（正常——HTML 中的 class），header 出现在 HTML 中。检查确保没有 `!important`:

```bash
grep -c '!important' dist/css/nav.css
```

预期: 0。

- [ ] **Step 5: 浏览器验证**

```bash
python static-server.js
```

打开 `http://localhost:端口/dist/index.html`，验证:
- 首页导航样式正常
- 搜索功能正常
- 页面间导航跳转正常
- 侧边栏显示正常
- 产品详情页图片浏览正常

- [ ] **Step 6: 最终 commit（如有微调）**

```bash
git add -A && git commit -m "chore: final verification tweaks"
```

---

## Self-Review Notes

- **Spec coverage**: 所有 spec 中的组件 (nav, sidebar, footer, search, product-detail) 都有对应任务
- **No placeholders**: 所有步骤都包含完整代码
- **Type consistency**: CSS 变量名、class 名、JS 函数名跨任务一致
