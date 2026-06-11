# DEVELOPMENT.md — 华创生电机官网开发文档

> **用途**：换电脑后用 Claude Code 打开项目时，读取本文档即可无缝衔接开发。
> **维护规则**：每次完成有效开发或踩坑后，把关键发现更新到对应章节。本文档是活的，不是一次性的。

---

## 一、项目概述

华创生电机（HCS Motor）企业官网，德昌电机（JOHNSON ELECTRIC）授权代理商。

- **类型**：静态 HTML 网站 + 轻量后端
- **前端**：原生 HTML/CSS/JS，无框架，赛博朋克暗色主题（Orbitron + Share Tech Mono 字体）
- **构建**：Python `build.py` 将共享组件（nav/sidebar/footer）内联注入 HTML，CSS/JS 也内联化，输出到 `dist/`
- **开发服务器**：`serve.py`（Python HTTP 服务器，含表单/产品/分类/搜索 API）
- **后端 API**：FastAPI（`backend/main.py`，含产品 CRUD、MySQL 数据库）
- **部署目标**：静态站点（`dist/` 目录）+ 可选 FastAPI 后端

---

## 二、目录结构

```
HCSweb/
├── index.html                    # 首页（Banner 轮播、关于、产品六边形、新闻、联系表单）
├── products.html                 # 产品中心（侧边栏 Tab 切换 + 卡片网格）
├── product-detail-template.html  # 产品详情页模板（build.py 用占位符生成具体页面）
├── other-motor.html              # 其他马达子页面
├── throttle-motor.html           # 节气门马达子页面
├── turbo-motor.html              # 涡轮增压马达子页面
│
├── build.py                      # ★ 构建脚本：组件注入 + 详情页生成 + 静态资源复制
├── serve.py                      # ★ 开发/生产 HTTP 服务器（含 API、表单、图片上传、管理后台）
├── static-server.js              # 废弃的静态服务器（硬编码 Windows 路径）
│
├── inc/                          # 可复用的 HTML 组件片段
│   ├── nav.html                  #   导航栏（Logo + 链接 + 搜索框 + 下拉菜单）
│   ├── sidebar.html              #   产品侧边栏（分类 Tab 树）
│   └── footer.html               #   页脚（联系方式 + 微信弹窗 + 悬浮按钮）
│
├── css/                          # 样式（构建时内联为 <style>）
│   ├── common.css                #   CSS 变量、基础重置、通用动画
│   ├── nav.css                   #   导航栏全部样式（无 !important）
│   ├── sidebar.css               #   侧边栏样式
│   ├── footer.css                #   页脚 + 悬浮按钮 + 微信弹窗
│   ├── products.css              #   产品中心页特有样式
│   └── product-detail.css        #   产品详情页共享样式
│
├── js/                           # 脚本（构建时内联为 <script>，均为 IIFE 自包含）
│   ├── common.js                 #   移动菜单、平滑滚动、导航 active、微信弹窗、联系表单
│   ├── nav-search.js             #   Fuse.js 搜索（CDN 加载）
│   ├── sidebar.js                #   侧边栏 Tab 切换 + URL hash 同步
│   ├── product-detail.js         #   产品图片浏览（主图/缩略图切换）
│   └── track.js                  #   ★ 广告追踪（百度统计 + 来源解析 + 转化事件）
│
├── data/                         # 数据文件
│   ├── products.json             #   ★ 产品数据源（手动编辑或用管理后台）
│   ├── products.js               #   从 products.json 自动生成（前端 Fuse.js 搜索用）
│   ├── categories.json           #   分类/子分类/产品类型配置
│   ├── audit.json                #   管理后台操作审计日志
│   └── submissions.json          #   表单提交本地记录
│
├── images/                       # 原始图片资源
│   ├── logo.png / logo.jpg       #   网站 Logo
│   ├── banner-bg.jpg             #   Banner 背景图
│   └── products/                 #   产品图片（命名规则: {productId}_{8位uuid}.ext）
│
├── landing/                      # ★ SEM 落地页（无导航/侧边栏，单出口→转化）
│   ├── micro-switch.html         #   微动开关（主力）
│   ├── throttle-motor.html       #   节气门马达
│   ├── egr-motor.html            #   废气阀马达
│   ├── epb-motor.html            #   EPB马达
│   └── turbo-motor.html          #   涡轮增压马达
│
├── fonts/                        # 自托管字体（Google Fonts 国内不可用）
│   ├── fonts.css                 #   @font-face 声明
│   └── orbitron-*.ttf / share-tech-mono.ttf  # 6 个文件，共 ~130KB
│
├── dist/                         # 构建输出（部署目录）
│   ├── index.html                #   构建后的完整页面（组件已注入、CSS/JS 已内联）
│   ├── products.html
│   ├── product-*.html            #   从模板生成的详情页
│   ├── images/                   #   复制的图片
│   ├── fonts/                    #   复制的字体
│   └── data/
│       └── products.json         #   复制的产品数据（供前端 API 用）
│
├── backend/                      # FastAPI 后端（独立运行，非必须）
│   ├── main.py                   #   API 入口（CORS + 路由注册 + /admin）
│   ├── config.py                 #   MySQL 连接配置
│   ├── database.py               #   pymysql 连接封装
│   ├── admin.html                #   管理后台页面
│   └── routes/
│       └── products.py           #   产品 CRUD API（pymysql + raw SQL）
│
└── docs/                         # 文档
    ├── DEVELOPMENT.md            #   本文件：开发指南
    ├── claude-memory/            #   Claude Code 记忆文件（开发经验碎片）
    └── superpowers/              #   设计文档和 specs
        ├── plans/                #   实施计划
        └── specs/                #   设计规范
            ├── 2026-06-07-sem-marketing-system-design.md       # SEM 营销方案
            └── 2026-06-07-competitor-ranking-tracker.md       # 竞品排名追踪
```

---

## 三、开发工作流

### 3.1 启动开发服务器

```bash
# 方法一：serve.py（推荐，含 API 功能）
PYTHONIOENCODING=utf-8 python serve.py

# 方法二：纯静态服务器（快速预览，无 API）
cd dist && PYTHONIOENCODING=utf-8 python -m http.server 8080 --bind 0.0.0.0
```

访问：
- 首页：`http://localhost:8080/`
- 管理后台：`http://localhost:8080/admin`
- API：`GET /api/products`、`POST /api/contact` 等

### 3.2 构建

```bash
PYTHONIOENCODING=utf-8 python build.py
```

构建做的事：
1. 读取 `inc/*.html` 组件
2. 读取 CSS/JS 文件内容内联到 HTML
3. 正则替换 `<!-- #include ... -->` 占位符
4. 替换 `{{BUILD_TIME}}` 为构建时间戳
5. 从 `product-detail-template.html` + `products.json` 生成各产品详情页
6. 复制 `images/`、`fonts/` 到 `dist/`

### 3.3 修改代码后的标准流程

1. 修改源文件（HTML/CSS/JS/images）
2. 运行 `python build.py`（必须，否则 dist/ 不更新）
3. 如果 serve.py 正在运行，它会在产品数据变更时自动 build
4. 刷新浏览器（如果缓存问题，URL 加 `?v=随机数`）

### 3.4 端口冲突排查

如果页面异常（导航消失、布局乱），可能是多个服务器进程抢 8080 端口：

```bash
netstat -ano | grep 8080          # 查占用进程
taskkill /F /PID <pid>            # 清理残留进程
curl -s http://localhost:8080/ | grep "include"  # 验证：不应出现 <!-- #include
```

---

## 四、核心架构

### 4.1 占位符语法（build.py 处理）

| 占位符 | 作用 | 示例 |
|--------|------|------|
| `<!-- #include css:common,nav -->` | 内联 CSS 为 `<style>` | `<style>/* CSS 内容 */</style>` |
| `<!-- #include js:common,nav-search -->` | 内联 JS 为 `<script>` | `<script>/* JS 内容 */</script>` |
| `<!-- #include nav.html -->` | 注入 HTML 组件 | 替换为 `inc/nav.html` 内容 |
| `<!-- #include cards:车用马达 -->` | 生成产品卡片 | 匹配 `cat` 或 `subCat` 字段 |
| `{{BUILD_TIME}}` | 构建时间戳 | `v2026.06.10-14:30` |
| `{{PRODUCT_TITLE}}` 等 | 详情页占位符 | 从 `products.json` 填入 |

### 4.2 CSS/JS 内联策略

**为什么内联**：每个页面从 6-10 个 HTTP 请求降到 2 个（HTML + Fuse CDN），国内加载快。源码依然模块化，开发体验不变。

- CSS 占位符可以逗号分隔多个：`<!-- #include css:common,nav,footer -->`
- JS 同理：`<!-- #include js:common,nav-search,sidebar -->`
- 映射关系在 `build.py` 的 `CSS_MAP` 和 `JS_MAP` 字典中

### 4.3 产品数据模型（products.json）

```json
{
  "id": "1031001",                              // 唯一产品编号
  "title": "1031001涡轮增压执行器电机",           // 产品名称
  "cat": "车用马达",                             // 一级分类
  "subCat": "涡轮增压执行器马达",                 // 二级分类（子类目）
  "desc": "用于大通、长城等品牌...",              // 产品描述
  "url": "product-1031001.html",                // 详情页 URL（有 detail 或 detail_images 时自动生成）
  "images": ["images/products/xxx.png", ...],   // 主图列表（最多 6 张）
  "detail": "",                                 // 详情文字（可选）
  "detail_images": ["images/products/xxx.png", ...], // 详情图（最多 10 张）
  "productType": "12V有刷直流",                  // 产品类型
  "specs": {                                    // 规格参数（自由 key-value）
    "应用领域": "...",
    "安装位置": "..."
  },
  "cardImage": "images/products/1031001_card.png" // 卡片图（可选，优先于 images[0]）
}
```

**url 自动生成规则**（`serve.py` 中 `generate_url()`）：
- 有 `detail` 文字 OR 有 `detail_images` → `product-{id}.html`
- 都没有 → `products.html#tab-motor`

### 4.4 分类体系（categories.json）

```
车用马达 (car-motor)
├── 节气门马达
├── 废气阀马达
├── 涡轮增压执行器马达
├── 车门锁马达
├── EPB马达
└── 其他马达
家用电器及电动工具马达 (appliance)
├── 家用电器马达
└── 电动工具马达
微动开关 (switch)
└── 微动开关
```

### 4.5 导航路由

| Section ID | 页面 | 导航链接 href |
|-----------|------|-------------|
| `home` | index.html（Banner 区域） | `index.html` |
| `about` | index.html | `#about` |
| `products` | products.html | `products.html?v=...` |
| `news` | index.html | `#news` |
| `contact` | index.html | `#contact` |

**导航 active 逻辑**（`js/common.js` `updateNavOnScroll`）：
- 纯粹基于 section 匹配，无 fallback
- `#home` 和 `#products` 需要显式特殊处理（因为它们的 href 不是 `#xxx` 格式）
- 不命中任何 section 时不操作（避免 transition 抖动）

### 4.6 侧边栏路由

侧边栏点击 Tab → 切换 `product-tab-panel` + 更新 URL hash → `hashchange` 事件驱动

### 4.7 线索数据模型（leads 表）

落地页表单提交存入 MySQL `motor_website.leads` 表，`track.js` 自动注入广告来源字段：

```sql
CREATE TABLE leads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,   -- 客户姓名
    phone       VARCHAR(20)  NOT NULL,   -- 联系电话
    company     VARCHAR(200) DEFAULT '', -- 公司名称
    message     TEXT,                    -- 需求描述

    -- 广告追踪（track.js 自动注入）
    ad_platform  VARCHAR(20)  DEFAULT '',  -- baidu / bing
    ad_keyword   VARCHAR(200) DEFAULT '',  -- 搜索关键词
    ad_plan      VARCHAR(100) DEFAULT '',  -- 广告计划
    ad_bd_vid    VARCHAR(100) DEFAULT '',  -- 百度点击ID
    landing_page VARCHAR(200) DEFAULT '',  -- 来源落地页

    -- 跟进
    status      VARCHAR(20) DEFAULT 'new',  -- new/contacted/qualified/closed
    note        TEXT,                       -- 销售跟进备注
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4.8 追踪系统架构（track.js）

- **广告来源解析**：URL 参数 `?bd_vid=xxx&keyword=xxx`（百度）或 `?utm_source=bing&utm_campaign=xxx`（Bing）写入 localStorage
- **自动事件**：页面加载(`ad_landing`)、滚动深度(50%/75%/100%)、停留时长(30s/60s/120s)
- **点击事件**：`data-track` 属性驱动，零侵入（`tel_click`、`cta_click`、`form_submit`、`exit_link`）
- **表单注入**：提交时自动追加广告来源隐藏字段
- **平台扩展**：后期加 Bing/Google 追踪只需在 `send()` 函数加一行代码

---

## 五、已完成的重点工作

### 5.1 组件化重构（2026-05-31）
- CSS 从 7 个 HTML 内联重复 → 6 个独立 CSS 文件
- JS 从内联重复 → 4 个独立 JS 文件（IIFE）
- HTML 共享部分（nav/sidebar/footer）→ `inc/*.html`
- `build.py` 增强支持占位符替换和产品卡片动态生成
- **踩坑**：banner HTML 结构必须精确嵌套（`banner-content` 在 `banner-dark-bg` 内部），委托 subagent 容易搞错层级

### 5.2 CSS/JS 内联化（构建优化）
- 从 `<link>`/`<script src>` 改为直接内联到 `<style>`/`<script>` 标签
- HTTP 请求减少 70%+
- 构建后不需复制 css/js 目录到 dist

### 5.3 字体自托管
- Google Fonts（Orbitron + Share Tech Mono）国内不可用
- 下载 TTF → `fonts/` → `@font-face` → `build.py` 复制到 `dist/fonts/`
- CSS 字体回退链：`"Orbitron", "Microsoft YaHei", sans-serif` 和 `"Share Tech Mono", "Consolas", "Courier New", monospace`
- 共 6 个文件 ~130KB

### 5.4 Banner 六边形产品网格
- CSS container queries 自适应正方形容器
- 正六边形公式：`clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%)`
- w/h = 2/√3 ≈ 1.155，蜂窝步长：水平 0.75w，垂直 0.5h
- **核心坑**：缝隙 = 两倍单边缩量。基础尺寸 = 贴合尺寸 × (1 - (scale-1)/2)
- 移动端和桌面端用同一套百分比，container query 自动适配

### 5.5 Banner 3-Slide 轮播系统
- 3 个 slide 各有不同的动画主题（齿轮/磁感线SVG/能量波）
- JS 手动轮播 + 悬停暂停 + 触摸滑动
- **Slide 2 磁感线修复**：SVG 不能放在 `width:0; height:0` 容器内

### 5.6 导航下划线滚动监听
- **核心教训**：先查 HTML 结构再写匹配逻辑（`section#home` 存在但导航无 `href="#home"`）
- 不要用 fallback 掩盖问题，找到根因再改
- 精确匹配优先，特殊情况显式处理

### 5.7 管理后台（serve.py 内置）
- `/admin` — 产品 CRUD + 图片多选拖拽上传 + 分类编辑 + 审计日志
- `POST /api/contact` — 表单提交 + SMTP 邮件通知
- `POST /api/categories/save` — 分类配置持久化
- 自动 build：产品数据变更后自动运行 `build.py`
- 操作审计：自动记录增/删/改到 `audit.json`（保留最近 500 条）

### 5.8 产品详情页模板化
- `product-detail-template.html` + `{{占位符}}` → build.py 批量生成
- 支持：主图切换、缩略图导航、规格参数表、详情图展示
- 卡片图 `cardImage` 优先于 `images[0]`，无图时用 emoji 占位

### 5.9 编码和环境修复
- Windows GBK → `PYTHONIOENCODING=utf-8` 解决中文/emoji 乱码
- Python App Execution Alias 拦截 `python` 命令 → 删除 `WindowsApps` 下的快捷方式
- 多进程端口冲突 → `netstat` + `taskkill` 排查
- **系统级 UTF-8**：注册表 ACP 改为 65001，重启后 cmd/PowerShell/Git Bash 统一 UTF-8

### 5.10 SEM 营销方案设计（2026-06-07~08）

完成了完整的广告投流方案设计和竞品分析：

**竞品分析**：
- **永佳承（深圳）**：8 个 B2B 平台矩阵（医药网库、世环通、黄页88、中国制造网、供应商网、爱企查、1688、爱普搜汽车），纯自然 SEO，无付费广告。Bing SEO 强但百度弱。
- **博泰克（苏州）**：代理 13 个品牌，有英文站。"Saia Burgess"系关键词强。百度几乎无存在感，无付费广告。
- 两个竞品共通的死穴：无 HTTPS（部分）、无追踪代码、无专用落地页。

**方案产出**：
- [SEM 营销系统设计方案](superpowers/specs/2026-06-07-sem-marketing-system-design.md)（11 章）
- [竞品排名追踪基线](superpowers/specs/2026-06-07-competitor-ranking-tracker.md)（Bing 8 词 + 百度 7 词）

**关键决策**：
- 百度 50% + Bing 50% 双引擎，控制变量对比效果
- 微动开关主力 + 车用马达辅推 + 品牌防守
- 在线客服：试投期百度商桥（免费），放量期备选美洽/自建

### 5.11 产品数据防泄漏（2026-06-11）

审计发现产品数据在三个载体中暴露：

| 载体 | 路径 | 泄露方式 |
|------|------|----------|
| `products.json` | `dist/data/products.json` | serve.py 的 `regenerate_js()` 写入，浏览器直接访问 |
| `products.js` | `data/products.js`（git 跟踪） | 含完整 `var PRODUCTS_DATA = [...]`，仓库历史永久泄露 |
| `/api/products` | HTTP 端点 | 无认证，脚本可批量抓取（后续加 Basic Auth） |

**修复**：
- 删除 `regenerate_js()` 函数（搜索已切到 `/api/search` API，此函数已死）
- `git rm` + `.gitignore` 移除 `products.js`
- `rm -rf dist/data/` 清除残留静态文件
- `/api/products` 端点认证留给 P2-3（管理后台安全加固）

**连带发现**：`regenerate_js()` 只把 `products.json` 写入 `dist/data/`，从未把 `products.js` 写入 `dist/`。如果 Fuse.js 搜索还在用，早就坏了——幸好已切到 API 方案。

详情：[防泄漏实施方案](IMPLEMENTATION-DATA-LEAK.md)

### 5.12 图片拖拽排序 + 卡片图裁剪（2026-06-11）

**拖拽排序修复**（3 个 bug + 1 个 Chromium 缺陷）：

| Bug | 现象 | 根因 | 修复 |
|-----|------|------|------|
| 跨网格污染 | 上传详情图刷新主网格 | `addFilesToGrid()` 硬编码 `mainImgGrid` | 改为调用侧传 `gridId` 参数 |
| 跨网格拖放 | 主图拖到详情网格破坏数组 | `ondrop` 无校验 | 加 `parentElement` 同网格检查 |
| 部分图片拖不动 | 产品间表现不一致 | **双层根因**：① `<img>` 原生拖拽拦截 `<div>` dragstart ② Chromium 对 `naturalWidth ≥ 2686px` 的图片预览生成失败 | `img.draggable = false` + `setDragImage(1×1透明GIF)` |
| 移动端不可用 | 无触摸事件 | `touchstart/move/end` 未实现 | 追加触摸拖拽逻辑 |

**根因追查教训**：最初的"原生拖拽拦截"假设解释不了为什么小图可拖、大图不可拖。Playwright 测试发现分界线：≤1872px 可拖，≥2686px 不可拖。根因不止一个，是两层叠加。

**卡片图裁剪**：`object-fit: contain` → `cover`，`css/products.css` + `build.py` 各改 1 行。

详情：[IMAGE-IMPROVEMENT-PLAN.md](IMAGE-IMPROVEMENT-PLAN.md) / [图片拖拽不一致修复方案](图片拖拽不一致修复方案.md)

---

## 六、踩过的坑和关键教训

### 6.1 不要假设数据异常
- 发现 `products.json` 从 9 个变 3 个 → 先问用户，不要自行判定为"数据丢失"并恢复
- **原则**：看到的"异常"可能是用户有意为之。用 AskUserQuestion 确认后再动手

### 6.2 导航居中不要用绝对定位
- 屏幕变窄时 logo 和搜索会侵入居中区域
- 正确方案：保持原始 flex 布局，只在窄屏时缩小间距和字号

### 6.3 从 git 恢复样式
- 重构时样式被改坏 → `git show <commit>^:index.html` 找回原始版本
- `sed` 提取可能截断嵌套 `}`，大文件用 `sed -n '/start/,/end/p'` + 上下文验证

### 6.4 Subagent 使用边界
- 复杂 HTML 结构修改（如 banner 嵌套）不要委托 subagent
- CSS 定位 bug 亲自改
- 新文件创建可以委托

### 6.5 调试检查清单
1. F12 Computed 面板看实际 px 值
2. element.style 临时测试
3. Console 查 `window.innerWidth`
4. 验证 dist/ 文件确认 build.py 是否生效
5. URL 加 `?v=N` 绕过缓存
6. `pkill -f "http.server"` 重启服务器

### 6.6 Windows cmd 中文乱码
- **根因**：cmd.exe 默认 GBK（代码页 936），Git Bash 用 UTF-8，转换时乱码
- **根治**：`控制面板 → 区域 → 管理 → 更改系统区域设置 → 勾选 "Beta: 使用 Unicode UTF-8" → 重启`
- **注册表**：`HKLM\SYSTEM\CurrentControlSet\Control\Nls\CodePage\ACP` = `65001`
- **临时方案**：`cmd.exe /c "chcp 65001 >nul && <命令>"`

### 6.7 双载体数据泄露（2026-06-11 发现）

- **发现**：产品数据在两个载体中同时暴露：
  - `dist/data/products.json` — serve.py 写入，浏览器直接访问
  - `data/products.js` — git 跟踪，含 `var PRODUCTS_DATA = [...]`
- **根因**：搜索从 Fuse.js 改为 `/api/search` API 后，`products.js` 变成死代码，但 `regenerate_js()` 仍在维护它，且文件仍在 git 中
- **教训**：改数据访问方式时，要同时清理旧的数据载体。两处泄露（JSON + JS）都在原计划中被遗漏
- **修复**：删除 `regenerate_js()`、`git rm` products.js、`dist/data/` 不再写入产品 JSON

### 6.8 拖拽不一致的根因不是单层的（2026-06-11 发现）

- **现象**：同一管理后台的图片网格，部分图片可拖拽、部分不可。产品间表现不一致
- **最初判定**：`<img>` 原生拖拽拦截了 `<div>` 的 dragstart
- **不成立的原因**：如果仅此一个原因，小图也应该被拦截——但小图能拖
- **Playwright 测试揭示**：`naturalWidth ≤ 1872px` 的图可拖，`≥ 2686px` 的图不可拖。分界线与 `naturalWidth` 强相关
- **真正根因**：**双层叠加**——① `<img>` 原生拖拽（影响所有图）② Chromium 对大分辨率图片的拖拽预览生成失败（影响大图，静默取消 drag）
- **教训**：表现不一致 ≠ 根因只有一个。当一个假设解释不了所有现象时，用自动化测试（Playwright）批量检查 DOM 属性差异，而不是凭一条猜测反复试。`naturalWidth` 这个属性肉眼看不到，但测试能读到

---

## 七、开发约定

### 7.1 编码
- 所有文件 UTF-8
- 运行 Python 脚本必须带 `PYTHONIOENCODING=utf-8`
- 中文内容用 `ensure_ascii=False`

### 7.2 Python 环境
- Python 3.13：`C:/Users/11193/AppData/Local/Programs/Python/Python313/python.exe`
- 依赖：`fastapi`、`uvicorn`、`pymysql`（无 requirements.txt）

### 7.3 CSS 约定
- 所有颜色走 CSS 变量（定义在 `common.css`）
- 导航/侧边栏/页脚样式完全在各自 CSS 文件中，无 `!important`
- 移动端响应式在各自 CSS 文件的 `@media` 中处理

### 7.4 JS 约定
- 全部 IIFE 自包含，不互相依赖
- 全局变量不冲突
- `DOMContentLoaded` 入口统一

### 7.5 Git 约定
- 用户主动说"提交""推送" → 直接执行，不弹窗确认
- 非用户主动发起的 git 操作 → 先确认

### 7.6 开发前确认
- 收到任务 → 先复述理解 → 单选项弹窗"开始干活" → 用户回车 → 执行
- CSS 修改后自动 `python build.py`，不询问



### 7.7 文件编辑安全标准

**背景**：`.git` 目录被沙箱施加了 DENY 写权限，`git add`/`git commit` 不可用。因此用备份机制替代 git 的版本恢复能力。

**规则**：

1. **每次编辑前**必须备份原始文件，不论改动大小：
   ```powershell
   Copy-Item docs/IMPROVEMENT-PLAN.md "docs/IMPROVEMENT-PLAN.md.bak.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
   ```

2. 在备份文件上执行修改，不在原文件上直接动刀：
   ```powershell
   Copy-Item target.md target.md.working
   # 在 target.md.working 上做所有修改
   # 验证通过后：
   Move-Item -Force target.md.working target.md
   ```

3. 修改完成后验证关键结构（标题、条目编号）：
   ```powershell
   Get-Content target.md | Select-String "^### P0-"   # 确认所有 P0 项都在
   ```

4. 验证通过后合并覆盖原文件，保留最近 3 个备份，删掉更早的。

**不当操作示例**（2026-06-11 教训）：
```powershell
# ❌ 坏 — 在原文上直接做范围删除，匹配到错误位置，不可恢复
$lines = Get-Content file.md
$start = (Select-String "**验收标准**：" file.md)[0].LineNumber  # 匹配了第一个，不是目标
# ... 删除 $start 到 "**预估**：30 分钟" — 删掉了整个 P0-P1 段
Set-Content file.md $lines  # 直接覆盖，无法恢复
```

---

## 八、待办事项

### 🔴 P0 — 上线前
1. 网站部署（服务器/域名）
2. 全站字号加大（客户群体偏年长）
3. 移动端适配优化
4. 404/错误页面
5. 首页六边形填入实际产品图

### 🟡 P1 — 上线后
6. SEO 优化（TDK、sitemap、结构化数据、alt 标签）
7. SEM 营销系统实施（见 [方案文档](superpowers/specs/2026-06-07-sem-marketing-system-design.md)）：
   - track.js 追踪系统开发
   - 5 个落地页（landing/micro-switch.html 等）
   - /api/lead 后端 + leads 表
   - 百度统计 + 百度商桥接入
   - 百度 SEM + Bing Ads 开户投放
8. 百度爱采购 + B2B 平台矩阵入驻
9. 在线询价系统
10. 竞品排名月度跟踪（见 [竞品追踪](superpowers/specs/2026-06-07-competitor-ranking-tracker.md)）：永佳承（B2B×8）、博泰克（英文品牌词）

### 🟢 P2 — 功能增强
10. 产品对比功能
11. 管理页面安全加固
12. 客户访问信息记录

### 🔵 P3 — 后期
13. 英文版/多语言
14. 数据备份机制
15. 多用户登录 + 操作日志分类

---

## 九、如何更新本文档

每次完成有效的开发工作或踩坑后，把关键信息追加到对应章节：

- **新功能** → 添加到第五章"已完成的重点工作"
- **新坑** → 添加到第六章"踩过的坑和关键教训"
- **架构变化** → 更新第四章"核心架构"和第二章"目录结构"
- **新约定** → 更新第七章"开发约定"
- **待办变化** → 更新第八章

原则：让换一台电脑的 Claude Code 读完后，不需要重新踩你已经踩过的坑。

---

> 最后更新：2026-06-11
