---
name: refactoring-lessons
description: HTML组件化重构中踩过的坑和关键经验（含具体代码和步骤）
metadata: 
  node_type: memory
  type: project
  originSessionId: 967824f8-d5a7-465d-a2e4-3c94eea347f4
---

## 一、重构目标和方法

**问题**：7 个 HTML 页面，CSS/JS 全部内联重复 3-7 次。改一个样式要改 7 个文件，经常漏改，补丁上打补丁。

**方案**：CSS/JS 抽离为独立文件，HTML 组件抽离为 inc/*.html 片段，build.py 构建时注入。

**新增文件**：
```
css/common.css          — CSS变量 + 基础重置 + 通用动画
css/nav.css             — 导航栏全部样式（含搜索框，无 !important）
css/sidebar.css         — 侧边栏样式
css/footer.css          — 页脚 + 悬浮按钮 + 微信弹窗
css/products.css        — 产品中心页特有样式
css/product-detail.css  — 产品详情页共享样式
js/common.js            — 移动菜单、平滑滚动、导航active、微信弹窗、表单
js/nav-search.js        — 搜索逻辑（Fuse.js初始化和查询）
js/sidebar.js           — 侧边栏Tab切换、URL hash同步
js/product-detail.js    — 产品图片浏览（主图切换、缩略图、前后翻）
inc/sidebar.html        — 侧边栏纯HTML片段
inc/footer.html         — 页脚纯HTML片段
```

**页面引入清单**（通过 `<!-- #include -->`）：
- index.html: CSS=common,nav,footer | HTML=nav,footer | JS=common,nav-search
- products.html: CSS=common,nav,sidebar,footer,products | HTML=nav,sidebar,footer | JS=common,nav-search,sidebar
- product-*.html: CSS=common,nav,sidebar,footer,product-detail | HTML=nav,sidebar,footer | JS=common,nav-search,sidebar,product-detail

---

## 二、build.py 占位符语法

```html
<!-- #include css:common,nav,footer -->     → <link rel="stylesheet" href="css/common.css"> ...
<!-- #include js:common,nav-search -->      → <script src="js/common.js"></script> ...
<!-- #include nav.html -->                  → 注入 inc/nav.html 内容
{{BUILD_TIME}}                             → 构建时间戳
```

build.py 核心逻辑：
1. 读取 inc/*.html 组件文件
2. 正则匹配 `<!-- #include css:... -->` 替换为 `<link>` 标签
3. 正则匹配 `<!-- #include js:... -->` 替换为 `<script>` 标签
4. 字符串替换 `<!-- #include xxx.html -->`
5. 替换 `{{BUILD_TIME}}` 为当前时间
6. 复制 css/ js/ images/ data/ 到 dist/

---

## 三、Banner 3-Slide HTML 结构（必须精确嵌套）

```
<div class="banner-slide active">
    <div class="banner-slide-bg">          ← flex row 容器
        <div class="banner-dark-bg">       ← 左侧 flex:1（深色区）
            <div class="banner-motor-bg">  ← 动画元素容器
                ...gears/circuit-lines/magnetic-field/energy-waves...
            </div>
            <div class="banner-content">   ← 文字覆盖层（必须在 dark-bg 内）
                <h1 class="banner-title">标题</h1>
                <p class="banner-subtitle">副标题</p>
                <a class="banner-btn">按钮</a>
            </div>
        </div>
        <div class="banner-gold-bg">       ← 右侧 width:45%（金色区）
            <div class="banner-product-grid">
                ...7个六边形...
            </div>
        </div>
    </div>
</div>
```

**关键规则**：
- `banner-content` 和 `banner-gold-bg` 都必须是 `banner-slide-bg` 的直接子元素
- `banner-content` 必须嵌套在 `banner-dark-bg` 内部（文字覆盖深色区）
- 如果 `banner-content` 跑到 `banner-slide-bg` 外面，flex 左右布局会失效
- `banner-motor-bg` 有 `overflow: hidden` 用来裁剪齿轮动画溢出

**三个 Slide 内容**：
- Slide 1: 齿轮动画（motor-gear gear-1/2/3）+ 电路线（circuit-lines）+ 文字"华创生电机"
- Slide 2: 磁感线SVG（magnetic-field-lines）+ 文字"专注自动化驱动20年"
- Slide 3: 脉冲（motor-pulse）+ 能量波（energy-waves）+ 文字"品质源于专业"

**Slide 2 磁感线 SVG 修复**：
- SVG 不能在 `width:0; height:0` 的 `.magnetic-field` 容器内（百分比宽高会计算为 0）
- 修复：把 `.magnetic-field-lines` 提到 `.magnetic-field` 外面，作为 `.banner-motor-bg` 的直接子元素
- SVG 设为 `width: 100%; height: 100%`，viewBox 裁紧为 `0 -25 600 600`（原版 652×688 有大量空白）

---

## 四、CSS 变量体系 (common.css)

```css
:root {
    --color-primary: #005d73;      --color-accent: #00f5ff;
    --color-highlight: #ff2d78;    --color-gold: #d4a84b;
    --bg-primary: #050810;         --bg-nav: rgba(5,8,20,0.92);
    --text-primary: #ffffff;       --text-secondary: rgba(255,255,255,0.7);
    --font-display: "Orbitron", monospace;
    --font-body: "Share Tech Mono", monospace;
    --glow-text: 0 0 8px #00f5ff, 0 0 16px #00f5ff, 0 0 32px #00f5ff;
    --nav-height: 80px;            --sidebar-width: 220px;
}
```

---

## 五、导航栏重构要点

- `inc/nav.html` 从原来的 HTML+内联`<style>`改为**纯HTML**，所有样式移到 `css/nav.css`
- 去掉所有 `!important` —— 因为 nav.css 是唯一导航样式源，没有优先级竞争
- 搜索框 HTML 留在 nav.html，CSS 在 nav.css，JS 在 nav-search.js
- 版本标签改用 `{{BUILD_TIME}}` 占位符
- 移动端响应式在 nav.css 的 `@media (max-width: 768px)` 处理
- 搜索使用 Fuse.js (CDN) + data/products.js 数据

---

## 六、JS 文件职责

| 文件 | 功能 |
|------|------|
| common.js | DOMContentLoaded入口、移动菜单切换、平滑滚动、导航active(URL+scroll)、微信弹窗、联系表单 |
| nav-search.js | 搜索输入监听、Fuse初始化、结果渲染、点击外部关闭、Escape关闭 |
| sidebar.js | 侧边栏Tab点击切换、URL hash同步、二级菜单hover |
| product-detail.js | 产品主图/缩略图切换、前后翻按钮 |

每个JS都是IIFE自包含，不互相依赖。全局变量不冲突。

---

## 七、Python 环境配置

- Python 3.13 路径：`C:/Users/11193/AppData/Local/Programs/Python/Python313/python.exe`
- Windows App Execution Alias（`C:\Users\11193\AppData\Local\Microsoft\WindowsApps\python.exe`）会拦截 python 命令，用 PowerShell `Remove-Item` 删掉
- bash 里设置 `export PYTHONIOENCODING=utf-8` 解决中文乱码
- 快捷方式：`export PATH="/c/Users/11193/AppData/Local/Programs/Python/Python313:$PATH"`
- 启动本地服务器：`cd dist && python -m http.server 8080 --bind 0.0.0.0`

---

## 八、调试方法

1. **F12 Computed 面板**：选中元素后看实际渲染的 px 值，不要只看 CSS 源码中的百分比/calc
2. **element.style 临时测试**：直接在浏览器加 `margin: auto`、`margin-top: 50px` 等看效果，即时生效
3. **Console 查视口宽度**：`window.innerWidth`
4. **验证 costruito 是否更新**：直接看 dist/ 目录下的文件内容，确认 build.py 是否生效
5. **强制绕过缓存**：URL 加 `?v=N` 参数
6. **重启服务器**：代码改了但页面没变时 `pkill -f "http.server"` 然后重新启动

---

## 九、Subagent 使用经验

- 复杂 HTML 结构修改（如 banner 嵌套）不要委托 subagent，容易搞错 `</div>` 层级
- 如果委托，必须给出**完整精确的替换代码**，不能只说"修复 XX"
- CSS 定位 bug 亲自改，subagent 难以理解布局上下文
- 新文件创建（如 css/*.css）委托给 subagent 可以，因为内容是确定的

---

## 十二、导航栏居中踩坑

**结论：不要用绝对定位居中导航链接。** 屏幕变窄时 logo 和搜索会侵入居中区域，造成重叠。

正确方案：
1. 导航链接保持原始 flex 布局（logo absolute left, nav flex, spacer, search fixed right）
2. 不加 `justify-content: center`，不改变 nav 的布局方式
3. 只在窄屏时缩小间距和字号防止重叠

```css
/* 中间断点：1500px 以下收紧间距 */
@media (max-width: 1500px) {
    .logo { left: 10px; }
    .logo-text { font-size: 28px; }
    .nav-link { padding: 0 10px; font-size: 14px; letter-spacing: 0; }
    .nav-search { right: 10px; }
    #nav-search-input { width: 80px; }
}
```

**How to apply:** 导航居中问题不要动 flex 结构，只调断点间距。

## 十三、从 git 历史恢复原始样式

重构时部分样式被改成了浅色主题（about/news/contact/banner），颜色和字体全丢。

恢复方法：`git show <refactor-commit>^:index.html` 查看前一个版本的完整 CSS，逐个对比恢复。

**注意**：`sed -n '/\.selector/,/}/p'` 可能截断嵌套的 `}`，大文件用 `sed -n '/start/,/end/p'` 配合上下文验证。

**How to apply:** 任何重构后样式对不上的问题，用 `git show commit^:file` 找回原始版本。

---

## 十一、待处理问题

1. **移动端六边形适配**：目前桌面端用固定 470×490，移动端 (≤768px) 用 `padding-bottom` hack + 百分比。移动端 item 位置还需验证
2. **页面性能**：重构后 HTTP 请求从 1 个变成 6-7 个（外部 CSS/JS），用户反馈可能变慢，待进一步优化（方案：构建时内联 CSS/JS）
3. **其他 4 个页面**：product-1030896.html、other-motor.html、throttle-motor.html 已重构但未全面测试
