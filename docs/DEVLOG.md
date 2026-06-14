# DEVLOG.md — 开发日志

> **定位**：按时间顺序记录每次有效开发工作的内容、方法和踩坑。不替代开发文档。
> **读者**：团队成员回顾历史决策、新成员了解项目演进。
> **维护**：每次完成有效开发后，在对应章节追加一条。标题精确到秒（`HH:MM:SS 事项`）。不需要提前规划。

---

## 2026年6月

### 6月13日：文档规范化

- **拆出 DEVLOG.md**：将 DEVELOPMENT.md 中混杂的开发日志（§5 已完成工作 + §6 踩坑）提取为独立文件
- **DEVELOPMENT.md 精简**：从 11 章缩减为 8 章，聚焦架构、约定、部署
- **IMPROVEMENT-PLAN.md 状态更新**：已完成项标记 `[x]`

### 6月13日：serve.py 安全审计 + 修复

**手写 multipart 解析器审计**：

| 问题 | 严重度 | 状态 |
|------|--------|------|
| Content-Length 无上限校验 → `rfile.read(content_length)` 直接按声明读入内存，恶意 1GB 可致 OOM | 🔴 | 待修复 |
| `body.split(boundary)` 在二进制数据中误匹配 → 文件损坏 | 🟡 | 待修复 |
| 文件以 `\r\n` 结尾 → 尾部被误剥离 | — | 确认不存在 |
| 5MB 随机数据完整性 | — | 通过 |
| 空文件名处理 | — | 正确 |

以上两项待修复已加入 `docs/TODO.md`。

**auto_build() 阻塞修复**：

- **根因**：`save_products()` → `auto_build()` → `subprocess.run(build.py, timeout=30)` 同步执行
- **服务器**：`http.server.HTTPServer` 纯单线程，构建期间所有请求排队
- **实测**：构建 ~0.5s（4 产品），timeout 窗口 30s
- **修复**：`auto_build()` 改为 `threading.Thread(target=auto_build, daemon=True).start()` 后台异步，响应立即返回，构建完成后 dist/ 自动更新

### 6月13日：记忆系统整理

- **待办清单**：从 Claude memory 迁至项目仓库 `docs/TODO.md`（跨设备可见）
- **项目技术知识**：5 个文件从 memory 迁至 `docs/项目技术知识/`（构建字体、六边形布局、导航调试、端口排查、重构经验）
- **删除重复记忆**：`commit-permission-rule.md`、`commit-without-confirm.md`（内容重复）
- **memory 精简**：保留 4 个用户偏好文件

### 6月14日：卡片图 Canvas 处理三轮迭代 + 最终方案

**背景**：CSS 图片区占比从 42% 调大到 71.9%，同时 1061418 新上传卡片图出现三个问题：背景不透明变纯白、电机过度放大、主体显示不全。

**第一轮 — 定位原罪**（`handleCardImgSelect()` 旧代码两处破坏）：

| 操作 | 代码 | 后果 |
|------|------|------|
| 白底填充 | `ctx.fillStyle='#ffffff'; fillRect(0,0,w,h)` | PNG 透明通道全毁，alpha 变 255 |
| 15% 留白 | `padding = min(w,h)*0.15; canvas 放大 + drawImage 居中` | 电机在画面中占比缩小 |

**像素证据**：旧卡片图四角 `(0,0,0,0)` 透明，新上传四角 `(255,255,255,255)` 不透明白。

**第二轮 — 去掉破坏 + 自动裁边**：
- 去掉白底填充和 15% 留白
- 新增采样扫描透明边界（stride = min(w,h)/400）
- 裁掉透明留白后输出正方形（10% 边距）

**第三轮 — centering bug**：裁剪方案用 `cropX/cropY` + `Math.min(cropY, h-side)` 边界钳制，当源图电机偏下时，钳制将正方形贴底 → 电机偏下。1031001 实测：上留白 64%，下留白 0%。

**终版 — 提取内容 + 居中绘制**：
```javascript
// 不再裁剪，改为提取内容区域居中绘制到新画布
var dx = Math.round((side - contentW) / 2);
var dy = Math.round((side - contentH) / 2);
ctx.drawImage(tmpCanvas, cmin, rmin, contentW, contentH, dx, dy, contentW, contentH);
```
无论源图内容在什么位置，输出始终完美居中。

**经验教训**：

| # | 教训 | 详情 |
|---|------|------|
| 1 | 裁剪+钳制边界方案在边缘情况必偏 | 内容偏上/下/左/右时，`Math.min(crop, w-side)` 会把正方形推向对侧。提取+居中绘制不受源图内容位置影响 |
| 2 | 浏览器缓存 JS 导致"修复无效"假象 | 服务器读磁盘最新文件，但浏览器缓存旧 JS。多进程残留 + 无 Cache-Control 头加剧此问题。解决：硬刷新 + 杀掉旧进程 |
| 3 | 源图选错导致"反复修复同一问题" | 用户反复上传已被旧代码损坏的白底图，Canvas 正确保留了它。视觉上"没修好"是因为源图本身就是坏的 |
| 4 | Canvas 透明保留 = 不 fillRect 即可 | Canvas 初始全透明 `(0,0,0,0)`，drawImage 保留 alpha。`toBlob('image/png')` 输出带 alpha 的 PNG。不需要任何额外操作 |

**处理流水线终态**：
```
用户选择卡片图
  → 绘制到临时 Canvas，采样扫描非透明边界
  → 提取内容区 (cmin, rmin, contentW, contentH)
  → 计算正方形边长 = max(contentW, contentH) + 10% 边距
  → 居中绘制到新透明 Canvas
  → toBlob('image/png') 输出
```

### 6月14日：未引用图片清理

- 18 个文件未被 `products.json` 引用，移至 `images/unused/`，共 ~20 MB
- 删除重复 `logo.jpg`（仅 `logo.png` 被引用，两者完全一致，各 587 KB）
- dist 同步清理（build.py 重拷 images/）

### 6月14日：图片归类整理 — 三级分类目录 + 统一命名

- **目录结构**：`images/products/{一级分类}/{二级分类}/{产品ID}/`
  - 全部分类预先建好目录（3 大类 9 子类），空目录 `.gitkeep` 占位
  - 现有 4 个产品归入 `车用马达/` 下的对应子类
- **统一命名**：`{产品ID}_{位置}.{扩展名}`
  - `card` → 卡片图 / `main1/2/3` → 主图 / `detail1/2` → 详情图
- **serve.py 适配**：`save_uploaded_image()` 新增 `suffix` + `cat` + `subCat` 参数，上传自动归入对应三级目录并使用规范文件名。同名覆盖不积压
- **build.py**：无需修改，`shutil.copytree` 递归复制，子目录结构自动同步

### 6月13日：图片资源瘦身

- **总览**：`images/` + `dist/images/` 各 78 MB，共 ~156 MB
- **孤图清理**：23 个文件未被 `products.json` 引用（旧上传残留），删除后释放 43.4 MB × 2 = 87 MB
  - 最大单文件：`1030837-main3.png` 15.9 MB（已被 `.jpg` 版本替代）
  - 1061418 残留 7 个旧 PNG 共 18.9 MB，1031001 残留 12 个共 8.6 MB
- **依赖检查**：全项目 `grep` 确认 23 个孤图零引用（HTML/CSS/JS/JSON/PY），安全删除
- **残留问题**（待后续）：
  - 在引用图仍偏大：`banner-bg.jpg` 6 MB、`1030837-main2.jpg` 3.3 MB、多张 chart.png 2-3 MB
  - `logo.jpg` + `logo.png` 各 587 KB，重复

---

## 2026年6月11日

### 产品数据防泄漏

**发现**：产品数据在三个载体中暴露：

| 载体 | 路径 | 泄露方式 |
|------|------|----------|
| `products.json` | `dist/data/products.json` | serve.py 的 `regenerate_js()` 写入，浏览器直接访问 |
| `products.js` | `data/products.js`（git 跟踪） | 含完整 `var PRODUCTS_DATA = [...]`，仓库历史永久泄露 |
| `/api/products` | HTTP 端点 | 无认证，脚本可批量抓取 |

**修复**：
- 删除 `regenerate_js()` 函数（搜索已切到 `/api/search` API，此函数已死）
- `git rm` + `.gitignore` 移除 `products.js`
- `rm -rf dist/data/` 清除残留静态文件
- `/api/products` 端点认证留给 IMPROVEMENT-PLAN.md P2-3

**连带发现**：`regenerate_js()` 只把 `products.json` 写入 `dist/data/`，从未把 `products.js` 写入 `dist/`。如果 Fuse.js 搜索还在用，早就坏了——幸好已切到 API 方案。

**教训**：改数据访问方式时，要同时清理旧的数据载体。两处泄露（JSON + JS）都在原改进计划中被遗漏。

### 图片拖拽排序 + 卡片图裁剪

**拖拽排序修复**（3 个 bug + 1 个 Chromium 缺陷）：

| Bug | 现象 | 根因 | 修复 |
|-----|------|------|------|
| 跨网格污染 | 上传详情图刷新主网格 | `addFilesToGrid()` 硬编码 `mainImgGrid` | 调用侧传 `gridId` 参数 |
| 跨网格拖放 | 主图拖到详情网格破坏数组 | `ondrop` 无校验 | 加 `parentElement` 同网格检查 |
| 部分图片拖不动 | 产品间表现不一致 | **双层根因**：① `<img>` 原生拖拽拦截 `<div>` dragstart ② Chromium 对 `naturalWidth ≥ 2686px` 的图片预览生成失败 | `img.draggable = false` + `setDragImage(1×1透明GIF)` |
| 移动端不可用 | 无触摸事件 | `touchstart/move/end` 未实现 | 追加触摸拖拽逻辑 |

**根因追查教训**：最初的"原生拖拽拦截"假设解释不了为什么小图可拖、大图不可拖。Playwright 测试发现分界线：≤1872px 可拖，≥2686px 不可拖。根因不止一个，是两层叠加。

**卡片图裁剪**：`object-fit: contain` → `cover`，`css/products.css` + `build.py` 各改 1 行。

### 卡片图上传自动标准化

**问题**：`object-fit: cover` 后各产品卡片图填充程度不一致——1030896 刚好，1030837/1061418 太满。

**根因**：不同产品上传的卡片图比例各异（1.67~2.20），`cover` 对非匹配比例的图片裁剪过狠。

**方案**：上传时浏览器端 Canvas 自动处理——保持原比例 + 四周 15% 留白 + 白色背景。处理后效果等价于"给图片加了个相框"，任意比例上传后视觉统一。

**关键决策**：画布保持原图比例（非正方形）。理由是参照标准 1030896 本身是 2.20:1 横图——若强制正方形，参照标准会被自己否定。

---

## 2026年6月7日 ~ 8日

### SEM 营销方案设计

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

---

## 2026年5月31日

### 组件化重构

- CSS 从 7 个 HTML 内联重复 → 6 个独立 CSS 文件
- JS 从内联重复 → 4 个独立 JS 文件（IIFE）
- HTML 共享部分（nav/sidebar/footer）→ `inc/*.html`
- `build.py` 增强支持占位符替换和产品卡片动态生成
- **踩坑**：banner HTML 结构必须精确嵌套（`banner-content` 在 `banner-dark-bg` 内部），委托 subagent 容易搞错层级

---

## 更早的工作（日期未精确记录）

### CSS/JS 内联化（构建优化）
- 从 `<link>`/`<script src>` 改为直接内联到 `<style>`/`<script>` 标签
- HTTP 请求减少 70%+
- 构建后不需复制 css/js 目录到 dist

### 字体自托管
- Google Fonts（Orbitron + Share Tech Mono）国内不可用
- 下载 TTF → `fonts/` → `@font-face` → `build.py` 复制到 `dist/fonts/`
- CSS 字体回退链：`"Orbitron", "Microsoft YaHei", sans-serif` 和 `"Share Tech Mono", "Consolas", "Courier New", monospace`
- 共 6 个文件 ~130KB

### Banner 六边形产品网格
- CSS container queries 自适应正方形容器
- 正六边形公式：`clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%)`
- w/h = 2/√3 ≈ 1.155，蜂窝步长：水平 0.75w，垂直 0.5h
- **核心坑**：缝隙 = 两倍单边缩量。基础尺寸 = 贴合尺寸 × (1 - (scale-1)/2)

### Banner 3-Slide 轮播系统
- 3 个 slide 各有不同的动画主题（齿轮/磁感线SVG/能量波）
- JS 手动轮播 + 悬停暂停 + 触摸滑动
- **Slide 2 磁感线修复**：SVG 不能放在 `width:0; height:0` 容器内

### 导航下划线滚动监听
- **核心教训**：先查 HTML 结构再写匹配逻辑（`section#home` 存在但导航无 `href="#home"`）
- 不要用 fallback 掩盖问题，找到根因再改
- 精确匹配优先，特殊情况显式处理

### 管理后台（serve.py 内置）
- `/admin` — 产品 CRUD + 图片多选拖拽上传 + 分类编辑 + 审计日志
- `POST /api/contact` — 表单提交 + SMTP 邮件通知
- `POST /api/categories/save` — 分类配置持久化
- 自动 build：产品数据变更后自动运行 `build.py`
- 操作审计：自动记录增/删/改到 `audit.json`（保留最近 500 条）

### 产品详情页模板化
- `product-detail-template.html` + `{{占位符}}` → build.py 批量生成
- 支持：主图切换、缩略图导航、规格参数表、详情图展示
- 卡片图 `cardImage` 优先于 `images[0]`，无图时用 emoji 占位

### 编码和环境修复
- Windows GBK → `PYTHONIOENCODING=utf-8` 解决中文/emoji 乱码
- Python App Execution Alias 拦截 `python` 命令 → 删除 `WindowsApps` 下的快捷方式
- 多进程端口冲突 → `netstat` + `taskkill` 排查
- **系统级 UTF-8**：注册表 ACP 改为 65001，重启后 cmd/PowerShell/Git Bash 统一 UTF-8

---

## 踩坑索引

> 以下是从各次开发中提取的通用教训，按编号引用。

### 坑 1：不要假设数据异常
- 发现 `products.json` 从 9 个变 3 个 → 先问用户，不要自行判定为"数据丢失"并恢复
- **原则**：看到的"异常"可能是用户有意为之。先确认再动手

### 坑 2：导航居中不要用绝对定位
- 屏幕变窄时 logo 和搜索会侵入居中区域
- 正确方案：保持原始 flex 布局，只在窄屏时缩小间距和字号

### 坑 3：从 git 恢复样式
- 重构时样式被改坏 → `git show <commit>^:index.html` 找回原始版本
- `sed` 提取可能截断嵌套 `}`，大文件用 `sed -n '/start/,/end/p'` + 上下文验证

### 坑 4：Subagent 使用边界
- 复杂 HTML 结构修改（如 banner 嵌套）不要委托 subagent
- CSS 定位 bug 亲自改
- 新文件创建可以委托

### 坑 5：调试检查清单
1. F12 Computed 面板看实际 px 值
2. element.style 临时测试
3. Console 查 `window.innerWidth`
4. 验证 dist/ 文件确认 build.py 是否生效
5. URL 加 `?v=N` 绕过缓存
6. `pkill -f "http.server"` 重启服务器

### 坑 6：Windows cmd 中文乱码
- **根因**：cmd.exe 默认 GBK（代码页 936），Git Bash 用 UTF-8，转换时乱码
- **根治**：`控制面板 → 区域 → 管理 → 更改系统区域设置 → 勾选 "Beta: 使用 Unicode UTF-8" → 重启`
- **注册表**：`HKLM\SYSTEM\CurrentControlSet\Control\Nls\CodePage\ACP` = `65001`
- **临时方案**：`cmd.exe /c "chcp 65001 >nul && <命令>"`

### 坑 7：双载体数据泄露（2026-06-11）
- **教训**：改数据访问方式时，要同时清理旧的数据载体。两处泄露（JSON + JS）都在原计划中被遗漏

### 坑 8：拖拽不一致的根因不是单层的（2026-06-11）
- **教训**：表现不一致 ≠ 根因只有一个。当一个假设解释不了所有现象时，用自动化测试批量检查 DOM 属性差异，而不是凭一条猜测反复试

### 坑 9：浏览器端处理比服务端依赖更轻量（2026-06-11）
- **选择**：Card 图标准化用 Canvas（浏览器端），不走 Python PIL/Pillow（服务端）
- **教训**：能用浏览器原生 API 解决的问题，不要引入服务端依赖。`<canvas>` + `toBlob()` + `new File()` 这条链路覆盖了图片裁剪/缩放/格式转换的全部需求

### 坑 10：Canvas fillRect 会杀死 PNG 透明度（2026-06-14）
- **现象**：上传透明 PNG，结果背景变成纯白
- **根因**：`ctx.fillStyle='#ffffff'; ctx.fillRect(0,0,w,h)` 把整个画布涂成不透明白，再 `drawImage` 时透明区已被覆盖
- **教训**：Canvas 初始状态全透明 `(0,0,0,0)`，不需要任何填充。`toBlob('image/png')` 天然保留 alpha 通道。如果源图有透明背景，不要 fillRect

### 坑 11：裁剪 + 边界钳制在边缘情况必然偏位（2026-06-14）
- **现象**：自动裁边后电机偏下，上留白 64%、下留白 0%
- **根因**：`cropY = Math.min(centerY - side/2, h - side)` 在内容靠近源图边缘时把正方形推向对侧
- **教训**：提取内容区域 + 居中绘制到新画布（`drawImage(src, sx, sy, sw, sh, dx, dy, dw, dh)`）不受源图内容位置影响，比裁剪方案稳健

### 坑 12：浏览器缓存 JS 导致"修复无效"假象（2026-06-14）
- **现象**：改了 `admin.html`，上传仍走旧逻辑
- **根因**：① 浏览器缓存旧 JS（无 Cache-Control 头）② 多个 Python 进程残留监听 8080（Windows SO_REUSEADDR），请求可能路由到旧进程
- **教训**：改前端 JS 后，先 `taskkill` 杀光旧进程，重启服务，再硬刷新页面（Ctrl+F5）

---

> 最后更新：2026年6月14日
