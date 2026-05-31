# HTML 组件化重构设计文档

**日期**: 2026-05-31
**状态**: 设计中

---

## 1. 问题诊断

### 核心病灶：极端代码重复

当前项目有 7 个 HTML 页面，CSS 和 JS 全部内联在每个文件的 `<style>` 和 `<script>` 标签中，造成每份代码被复制 3-7 次。

| 重复内容 | 出现次数 | 位置 |
|----------|---------|------|
| 基础重置样式 (*, body, .container) | 7 | 每个 HTML 文件 |
| 导航栏 CSS (.header, .nav, .logo, .nav-link) | 7 | 每个 HTML + inc/nav.html |
| 搜索框 CSS (.nav-search, #nav-search-input, #nav-search-results) | 8 | 每个 HTML + inc/nav.html (!important 战争) |
| 侧边栏 HTML + CSS (.products-sidebar) | 3 | products.html, product-1030837.html, product-1030896.html |
| 页脚 HTML + CSS (.footer) | 多次 | 每个页面 |
| 搜索 JS (initNavSearch) | 7 | 每个 HTML |
| 轮播 JS | 2 | index.html, products.html |

### 后果

- **"改了 A 坏 B"**: 改一个页面的导航样式，其他 6 个页面仍是旧代码
- **CSS 优先级战争**: inc/nav.html 的 `<style>` 用 `!important` 覆盖页面样式，页面又用 `!important` 反制
- **版本号散落**: `v2026.05.25-13:30`、`v202604191751`、`v2026-05-18 22:41` 散布多个文件
- **新页面成本高**: 每加一个产品页需复制 ~500 行 CSS + ~200 行 JS

---

## 2. 方案选择

选用**方案 2: 组件 HTML + 独立 CSS/JS 文件**。

| 维度 | 决策 |
|------|------|
| 构建工具 | 增强现有 `build.py` (Python) |
| HTML 组件 | inc/*.html 纯 HTML 片段，通过占位符注入 |
| CSS | 独立 css/*.css 文件，页面通过 `<link>` 引入 |
| JS | 独立 js/*.js 文件，页面通过 `<script>` 引入 |
| 迁移策略 | 一步到位，新分支，3 个核心页面 (index, products, 一个产品详情页) 先改造 |
| 覆盖范围 | 全部 7 个页面，index-inline.html 合并到 index.html |

---

## 3. 目标目录结构

```
HCSweb/                          (仓库根目录，保持不变)
├── css/                         # 🆕 共享样式
│   ├── common.css               #   基础重置、CSS 变量 (颜色/字体/阴影)、通用动画
│   ├── nav.css                  #   导航栏样式 (logo, nav-link, 下拉菜单, 搜索框, 移动端)
│   ├── sidebar.css              #   侧边栏样式 (位置, hover, 子菜单, 响应式)
│   ├── footer.css               #   页脚样式 (布局, 颜色, 悬浮按钮)
│   ├── products.css             #   产品中心页特有 (Hero, Tab Panel, 产品卡片)
│   └── product-detail.css       #   产品详情页共享 (产品展示, 规格表, 图片浏览)
├── js/                          # 🆕 共享脚本
│   ├── common.js                #   移动菜单切换, 平滑滚动, 导航 active 统一管理, 微信弹窗
│   ├── nav-search.js            #   搜索输入, Fuse.js 初始化, 结果渲染, 键盘/失焦关闭
│   ├── sidebar.js               #   侧边栏 Tab 切换, URL hash 同步, 子菜单行为
│   └── product-detail.js        #   产品图片浏览 (主图切换, 缩略图, 前后翻)
├── inc/                         # 共享 HTML 片段
│   ├── nav.html                 #   导航栏 (纯 HTML, 去掉内联 <style>)
│   ├── sidebar.html             #   侧边栏 (纯 HTML)
│   ├── footer.html              #   页脚 (纯 HTML)
│   └── product-detail.html      #   (保留, 当前未使用, 后续扩展)
├── build.py                     # 增强: 多占位符 + CSS/JS 注入 + 资源复制
├── data/
│   └── products.js              # 产品搜索数据 (不变)
├── images/                      # 图片 (不变)
├── backend/                     # 后端 (不变)
│
├── index.html                   # 首页 (合并 index-inline.html, 精简)
├── products.html                # 产品中心 (精简)
├── product-1030837.html         # 产品详情 (精简, 模板化)
├── product-1030896.html         # 产品详情 (精简)
├── other-motor.html             # 其他马达 (精简)
├── throttle-motor.html          # 节气门马达 (精简)
└── dist/                        # 构建输出 (不变)
```

---

## 4. 组件设计

### 4.1 导航栏 (nav)

| 文件 | 内容 |
|------|------|
| `inc/nav.html` | 纯 HTML 结构: logo, nav-link×5, 下拉菜单, 搜索框, 版本号 |
| `css/nav.css` | 全部导航样式, **移除所有 !important** |
| `js/nav-search.js` | 搜索逻辑, 只写一次 |

**关键改动**:
- 去掉 `!important`: nav.css 是唯一导航样式源
- 搜索 CSS/JS 不再分散在各页面
- 版本号一处管理, build.py 构建时可自动更新
- 导航 active 高亮统一在 common.js 根据 URL 判断

### 4.2 侧边栏 (sidebar)

| 文件 | 内容 |
|------|------|
| `inc/sidebar.html` | 纯 HTML: 侧边栏结构 + 三个分类 + 子菜单 |
| `css/sidebar.css` | 全部侧边栏样式 (fixed 定位, hover, 子菜单展开, 响应式) |
| `js/sidebar.js` | Tab 切换, URL hash 同步, 子菜单行为 |

**关键改动**:
- 子菜单跳转统一使用 `<a href>` 而非 onclick
- active 状态由 JS 根据当前 URL/hash 自动设置
- 产品详情页保留侧边栏

### 4.3 页脚 (footer)

| 文件 | 内容 |
|------|------|
| `inc/footer.html` | 纯 HTML: 品牌信息, 快速链接, 产品链接, 服务链接, 版权, 悬浮按钮 |
| `css/footer.css` | 全部页脚样式 |

### 4.4 产品详情页模板

每个产品详情页结构一致，只保留产品独有内容:

```html
<!-- #include css:common,nav,sidebar,footer,product-detail -->
<!-- #include nav.html -->
<!-- #include sidebar.html -->

<main class="product-detail">
    <!-- 产品独有: 面包屑, 标题, 图片, 描述, 规格, 曲线图 -->
</main>

<!-- #include footer.html -->
<!-- #include js:common,nav-search,sidebar,product-detail -->
```

页面文件从 ~60KB 精简到 ~2KB（只有产品数据 + include 指令）。

---

## 5. build.py 改造

### 5.1 占位符语法

| 类型 | 语法 | 示例 |
|------|------|------|
| HTML 片段注入 | `<!-- #include xxx.html -->` | `<!-- #include nav.html -->` |
| CSS 引入 | `<!-- #include css:a,b,c -->` | `<!-- #include css:common,nav -->` |
| JS 引入 | `<!-- #include js:a,b,c -->` | `<!-- #include js:common,nav-search -->` |

### 5.2 处理流程

1. 读取所有 `inc/*.html` 片段
2. 遍历根目录 `*.html` 文件
3. 对每个文件:
   - 替换 `<!-- #include xxx.html -->` → 对应 HTML 片段内容
   - 替换 `<!-- #include css:a,b,c -->` → `<link rel="stylesheet" href="css/a.css">` × N
   - 替换 `<!-- #include js:a,b,c -->` → `<script src="js/a.js"></script>` × N
   - 替换版本号占位符 `{{BUILD_TIME}}`
4. 写入 `dist/`
5. 复制 `css/`, `js/`, `images/`, `data/` 到 `dist/`

### 5.3 版本号自动更新

`inc/nav.html` 中的版本标签改为占位符 `{{BUILD_TIME}}`，构建时替换为当前时间。

---

## 6. CSS 设计系统

### 6.1 变量定义 (common.css)

```css
:root {
    /* 主色调 */
    --color-primary: #005d73;
    --color-accent: #00f5ff;
    --color-highlight: #ff2d78;
    --color-gold: #d4a84b;
    /* 背景 */
    --bg-primary: #050810;
    --bg-nav: rgba(5, 8, 20, 0.92);
    --bg-card: rgba(0, 93, 115, 0.08);
    /* 文字 */
    --text-primary: #ffffff;
    --text-secondary: rgba(255, 255, 255, 0.7);
    --text-muted: rgba(255, 255, 255, 0.4);
    /* 字体 */
    --font-display: "Orbitron", monospace;
    --font-body: "Share Tech Mono", monospace;
    --font-fallback: "Microsoft YaHei", monospace;
    /* 发光效果 */
    --glow-text: 0 0 8px #00f5ff, 0 0 16px #00f5ff, 0 0 32px #00f5ff;
    --glow-strong: 0 0 12px rgba(0, 245, 255, 1), 0 0 24px rgba(0, 245, 255, 0.5);
    /* 间距 */
    --nav-height: 80px;
    --sidebar-width: 220px;
}
```

### 6.2 文件职责

| CSS 文件 | 职责 |
|----------|------|
| `common.css` | CSS 变量, `*`, `body`, `.container`, `@keyframes` (rotate, pulse, glow) |
| `nav.css` | `.header`, `.logo`, `.nav`, `.nav-link`, `.nav-dropdown`, `.dropdown-menu`, `.nav-search`, `.nav-version`, `.mobile-menu-btn`, 响应式 |
| `sidebar.css` | `.products-sidebar`, `.sidebar-nav-item`, `.sidebar-sub-items`, 响应式 |
| `footer.css` | `.footer`, `.footer-grid`, `.footer-bottom`, `.float-buttons`, `.wechat-modal` |
| `products.css` | `.page-hero`, `.products-layout`, `.products-content`, `.tab-panel-header`, `.product-card`, `.product-card-grid-sidebar` |
| `product-detail.css` | `.product-detail`, `.breadcrumb`, `.product-hero`, `.product-gallery`, `.product-info`, `.product-specs`, `.product-chart`, `.thumbnails` |

---

## 7. JS 职责划分

| JS 文件 | 职责 | 依赖 |
|----------|------|------|
| `common.js` | DOMContentLoaded 入口, 移动菜单, 平滑滚动, 导航 active, 微信弹窗, 表单提交 | 无 |
| `nav-search.js` | 搜索: Fuse 初始化, input 事件, 结果渲染, click-outside 关闭, Escape | Fuse.js (CDN), data/products.js |
| `sidebar.js` | 侧边栏 Tab 切换, URL hash 同步, 子菜单 hover 行为 | 无 |
| `product-detail.js` | 产品主图/缩略图切换, 前后翻按钮, 图片弹窗 | 无 |

每个 JS 文件自包含, 不互相依赖。global 变量不冲突。

---

## 8. 页面引入清单

### index.html

| 类别 | 引入 |
|------|------|
| CSS | common, nav, footer |
| HTML | nav.html, footer.html |
| JS | common, nav-search |

### products.html

| 类别 | 引入 |
|------|------|
| CSS | common, nav, sidebar, footer, products |
| HTML | nav.html, sidebar.html, footer.html |
| JS | common, nav-search, sidebar |

### product-1030837.html (模板代表)

| 类别 | 引入 |
|------|------|
| CSS | common, nav, sidebar, footer, product-detail |
| HTML | nav.html, sidebar.html, footer.html |
| JS | common, nav-search, sidebar, product-detail |

---

## 9. 详细实现步骤

1. **创建 CSS 文件** — 从现有页面提取, 替换硬编码颜色为 CSS 变量
2. **创建 JS 文件** — 从现有页面提取, 去重合并
3. **重写 inc/*.html** — 去掉 `<style>` 和 `<script>`, 只为纯 HTML, nav.html 版本号改占位符
4. **改造 build.py** — 支持多占位符和 CSS/JS 注入
5. **改造 index.html** — 合并 index-inline.html, 删除内联 CSS/JS, 改用 include
6. **改造 products.html** — 删除内联 CSS/JS, 改用 include
7. **改造 product-1030837.html** — 作为产品详情页模板, 删除内联 CSS/JS
8. **改造其余 4 个页面** — product-1030896.html, other-motor.html, throttle-motor.html
9. **删除 index-inline.html**
10. **构建测试** — `python build.py` 验证 dist/ 输出, 浏览器测试 3 个核心页面

---

## 10. 不变的内容

以下不做修改:
- `backend/` — 全部后端代码
- `data/products.js` — 产品搜索数据
- `images/` — 图片资源
- `static-server.js` — 本地预览服务器
- 页面中的**内容数据** — 产品描述、规格参数、图片路径等
- 外部 CDN 依赖 — Google Fonts, Fuse.js

---

## 11. 风险与回滚

- **风险**: CSS 优先级冲突。因为多个独立 CSS 文件加载, 选择器特异性可能导致样式覆盖差异
- **缓解**: CSS 变量统一控制颜色, 所有选择器严格限定在组件作用域内
- **回滚**: 在 git 新分支操作, 构建输出在 dist/, 不影响源文件。有问题直接切回 main 分支
