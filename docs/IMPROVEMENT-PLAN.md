<!--
  IMPROVEMENT-PLAN.md — 华创生电机官网改进路线图
  目标读者：任何 AI 编码代理（Codex、Claude Code、Copilot 等）
  用途：在新电脑上用新的 AI 工具打开项目时，读本文档 + AGENTS.md + DEVELOPMENT.md
         即可完整了解项目当前状态和改进方向，无缝衔接开发。

  本文档是结构化的，不是叙述性的。每个改进项包含：
  - 优先级（P0/P1/P2/P3）
  - 改什么（What）
  - 为什么（Why）
  - 验收标准（Done means）
  - 预估工时
  - 参考文档
-->

# 项目改进路线图

> **状态**：2026-06-11 基线评估
> **原则**：完成一个改进项后，将状态从 `[ ]` 改为 `[x]` 并注明日期。

---

## 改进前必读

在动手之前，AI 代理应先通读：

1. [AGENTS.md](/AGENTS.md) — 项目结构、运行时、约定
2. [DEVELOPMENT.md](/docs/DEVELOPMENT.md) — 完整开发指南（架构、占位符、教训）
3. [SEM 营销方案](/docs/superpowers/specs/2026-06-07-sem-marketing-system-design.md) — 为什么需要 track.js 和 landing/
4. [竞品排名追踪](/docs/superpowers/specs/2026-06-07-competitor-ranking-tracker.md) — 竞品数据上下文

---

## 🔴 P0 — 上线前必须完成（阻塞项）

### P0-1：添加 requirements.txt

- [ ] **待完成**

**改什么**：在仓库根目录创建 `requirements.txt`，锁定 Python 依赖。

**为什么**：当前项目没有声明 Python 依赖。在新电脑上无法复现开发环境。AGENTS.md 和 DEVELOPMENT.md 都标注了这个问题但未修复。

**验收标准**：
```
requirements.txt 包含：
  fastapi>=0.100.0
  uvicorn>=0.23.0
  pymysql>=1.0.0
  pydantic>=2.0.0

运行 `pip install -r requirements.txt` 后 backend/main.py 可正常启动。
```

**预估**：15 分钟

---

### P0-2：合并双后端，统一到 FastAPI

- [ ] **待完成**

**改什么**：消除 `serve.py`（stdlib HTTP）和 `backend/main.py`（FastAPI）之间的重复。将 serve.py 的所有功能迁移到 FastAPI，然后废弃 serve.py。

**为什么**：这是项目中最大的技术债务。两个后端各自维护独立的产品 CRUD、分类管理和 admin 面板实现，使用不同的数据存储（JSON 文件 vs MySQL）。SEM 营销方案已明确要求废弃 serve.py。

具体来说：

| 功能 | 当前在哪 | 目标 |
|------|---------|------|
| 产品 CRUD | serve.py (JSON) + backend/ (MySQL) | 仅 backend/ (MySQL) |
| 联系表单 + SMTP 邮件 | serve.py | 迁移到 backend/ |
| 图片上传 (multipart) | serve.py | 迁移到 backend/ |
| 分类管理 | serve.py (JSON) + backend/ (MySQL) | 仅 backend/ (MySQL) |
| 管理后台 /admin | serve.py 服务 backend/admin.html | 仅 backend/ 服务 |
| 搜索 API | serve.py | 迁移到 backend/ 或保持 JSON |
| 审计日志 | serve.py (audit.json) | 迁移到 backend/ (MySQL 表或保留 JSON) |
| 自动构建 | serve.py (产品保存后触发 build.py) | 迁移到 backend/ |

**验收标准**：
- 删除 `serve.py`（或重命名为 `serve.py.deprecated`）
- 单一命令即可启动全部功能：`python backend/main.py`
- `/admin` 管理后台在新后端下完全可用
- `POST /api/contact` 表单提交 + SMTP 邮件正常工作
- 产品图片上传正常工作
- 分类编辑正常工作
- 产品数据变更后自动触发 `build.py`
- DEVELOPMENT.md 第八章中 serve.py 相关的条目标注为已完成

**预估**：1-2 天

**关键注意事项**：
- 不要丢失 `serve.py` 中的 multipart 图片上传逻辑——`backend/routes/products.py` 目前不支持图片上传
- admin.html 从 `ADMIN_DIR` 加载，路径需从硬编码 Windows 路径改为相对路径
- `generate_url()` 函数需从 serve.py 移到共享模块
- `save_products()` 的自动构建钩子需保留
- SMTP 配置需从环境变量读取（当前 serve.py 的实现已经是这样）

---

### P0-3：移除硬编码的 Windows 路径

- [ ] **待完成**

**改什么**：修复 `backend/main.py` 中硬编码的 `ADMIN_HTML` 路径。

**为什么**：`ADMIN_HTML = r"C:\Users\11193\www\backend\admin.html"` 在其他任何电脑上都无法工作。DEVELOPMENT.md 称之为"环境特定"，但这会直接阻止部署。

**验收标准**：
```python
# backend/main.py 改为：
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ADMIN_HTML = os.path.join(BASE_DIR, "admin.html")
```

**预估**：5 分钟

---

### P0-4：移除死代码

- [ ] **待完成**

**改什么**：
- 删除 `static-server.js`（AGENTS.md 标记为"废弃的静态服务器"）
- 删除 `inc/nav.html.bak`（遗留备份文件）
- 将 `package.json` 的 `"main"` 从 `"static-server.js"` 更新为实际入口（或移除该字段）

**为什么**：死代码会让新来的 AI 代理困惑。它们必须阅读每个文件才能判断哪些是活的。AGENTS.md 已经标注了这些问题。

**验收标准**：
- `static-server.js` 已删除
- `inc/nav.html.bak` 已删除
- `package.json` 的 `"main"` 字段已更新或移除

**预估**：10 分钟

---

### P0-5：首页内容填充

- [ ] **待完成**

**改什么**：将首页占位内容替换为真实内容。

**为什么**：首页是门面。当前状态：
- **新闻板块**：假标题（"公司新闻标题"、"行业动态标题"）和表情符号替代图片
- **六边形产品网格**（`#products` section）：4 个表情符号（⚡🔧🏠🔘），一个真实产品图片都没有
- **关于我们**：表情符号 🏭 替代图片

DEVELOPMENT.md P0 #5 已要求"首页六边形填入实际产品图"。

**验收标准**：
- 新闻板块：至少 2 篇真实新闻文章，包含标题、日期和图片（或删除该板块）
- 六边形网格：每个六边形显示来自 `images/products/` 的实际产品图片，而非表情符号。链接到对应产品页或 `products.html`
- 关于我们：🏭 表情符号替换为公司照片或 logo

**预估**：2-4 小时（取决于需准备多少内容资产）

---

### P0-6：移动端适配

- [ ] **待完成**

**改什么**：审核并修复所有页面的移动端响应式问题。

**为什么**：DEVELOPMENT.md P0 #3 要求"移动端适配优化"。当前 index.html 有一些 `@media` 查询，但未系统验证。国内 B2B 客户大量使用手机浏览。

**验收标准**：
- 所有页面（index、products、product-detail、landing/*）在 375px 宽度下：无水平溢出、无文字重叠、表单输入框可用、导航菜单可用
- 产品卡片在移动端单列排列
- 联系表单按钮 ≥44px 触摸目标
- 确认 `index.html` 中 slide 2（磁感线 SVG）在移动端可见

**预估**：4-6 小时
---

## 🟡 P1 — 上线后立即推进（核心业务价值）

### P1-1：实现 SEM 营销系统

- [ ] **待完成**

**改什么**：按照 [SEM 营销方案](/docs/superpowers/specs/2026-06-07-sem-marketing-system-design.md) 构建整个追踪和落地页系统。

**为什么**：这是收入引擎。方案预估开发工时为 3 天，预算为每月 ¥3,000-5,000。竞品分析显示广告位完全开放——先发优势窗口不会永远敞开。

具体任务（按方案第十章的顺序）：

| 步骤 | 任务 | 预估 |
|------|------|------|
| 1 | 创建 `js/track.js`（~200 行，零依赖） | 0.5 天 |
| 2 | 创建 `backend/routes/leads.py` + MySQL `leads` 表 | 0.5 天 |
| 3 | 扩展 `backend/admin.html` 增加线索管理 Tab | 0.5 天 |
| 4 | 创建 `landing/` 目录 + 5 个落地页 | 1 天 |
| 5 | 扩展 `build.py` 支持落地页构建 | 0.5 天 |
| 6 | 集成百度统计 + 百度商桥（一行 JS 代码） | 0.5 天 |

**验收标准**：
- `js/track.js` 存在并实现方案第五章的全部功能（来源解析、自动事件、点击事件、表单注入）
- `POST /api/lead` 接受表单提交并写入 MySQL `leads` 表
- `landing/` 目录包含 5 个落地页，均按照方案第四章的布局设计
- 落地页通过 `build.py` 构建到 `dist/landing/`
- 百度统计代码注入到所有页面（通过 inc/footer.html）
- 管理员可在 `/admin` 查看线索列表（表格视图：姓名、电话、来源关键词、状态、时间）

**预估**：3 天

**参考文件**：
- [SEM 方案 — 第四章：落地页设计](/docs/superpowers/specs/2026-06-07-sem-marketing-system-design.md)
- [SEM 方案 — 第五章：追踪系统](/docs/superpowers/specs/2026-06-07-sem-marketing-system-design.md)
- [SEM 方案 — 第六章：数据存储](/docs/superpowers/specs/2026-06-07-sem-marketing-system-design.md)
- [SEM 方案 — 第十章：实施顺序](/docs/superpowers/specs/2026-06-07-sem-marketing-system-design.md)

---

### P1-2：SEO 基础优化

- [ ] **待完成**

**改什么**：为所有页面添加完整的 TDK（Title/Description/Keywords）、sitemap.xml、结构化数据和图片 alt 属性。

**为什么**：DEVELOPMENT.md P1 #6。竞品依赖自然 SEO——基础优化能以最小成本带来自然流量。当前 index.html 已有一个 meta description，但 products.html 和其他页面没有。永佳承的 B2B 矩阵方法表明关键词覆盖的重要性。

**验收标准**：
- 每个 HTML 页面：唯一的 `<title>`、`<meta name="description">` 和 `<meta name="keywords">`
- `/sitemap.xml` 列出所有公开页面
- 所有 `<img>` 标签包含描述性 `alt` 属性
- 首页使用 JSON-LD `Organization` 结构化数据
- 产品详情页使用 JSON-LD `Product` 结构化数据

**预估**：3-4 小时

---

### P1-3：添加更多产品数据

- [ ] **待完成**

**改什么**：将 `data/products.json` 从 3 个产品扩充到覆盖分类中更多子类目。

**为什么**：分类定义了 9 个子类目，但只有 3 个产品（全在"车用马达"下）。网站看起来空荡荡的。在投放 SEM 广告之前，每个落地页至少需要 1-2 个产品作为支撑。

**验收标准**：
- 至少 1 个"微动开关"产品 + 图片（SEM 主力落地页需要）
- 至少 1 个"家用电器及电动工具马达"产品 + 图片
- 每个产品包含完整的 `specs`、`desc` 和至少 1 张图片
- 产品图片放入 `images/products/`，命名规则：`{productId}_{8位uuid}.ext`

**预估**：4-8 小时（取决于产品数据准备的便利程度）
---

## 🟢 P2 — 功能增强（提升专业度与安全性）

### P2-1：全站字号加大

- [ ] **待完成**

**改什么**：将正文字号基线调大 1-2px，确保在年长客户群体中可读。DEVELOPMENT.md P0 #2。

**为什么**：客户群体偏年长（工业采购决策者）。赛博朋克主题使用 Share Tech Mono 和 Orbitron 字体——两者在小字号下都难以阅读。

**验收标准**：
- body `font-size` 从当前基线至少增大 1px
- 产品卡片描述文字 >= 14px
- 规格参数表文字 >= 14px
- 联系表单标签 >= 14px

**预估**：1-2 小时（在 common.css 中调整）

---

### P2-2：404 错误页面

- [ ] **待完成**

**改什么**：创建品牌化的 `404.html` 错误页面。DEVELOPMENT.md P0 #4。

**为什么**：用户输入错误 URL 或访问已删除的产品时会流失。一个友好的 404 页面能保留流量。

**验收标准**：
- `404.html` 存在于根目录（由 build.py 处理）
- 包含导航栏 + 页脚（与网站其他部分一致）
- 显示"页面未找到"中文消息 + 返回首页链接 + 产品搜索框

**预估**：30 分钟

---

### P2-3：管理后台安全加固

- [ ] **待完成**

**改什么**：在 `/admin` 路由前添加基本认证。DEVELOPMENT.md P2 #11。

**为什么**：产品数据是企业资产。目前 `/admin` 对任何知道该 URL 的人都完全开放。在产品上线前需要最低限度的保护。

**验收标准**：
- `/admin` 和所有 `/api/products` 修改端点（POST/PUT/DELETE）要求 HTTP Basic Auth
- 凭据通过环境变量配置（`ADMIN_USER`、`ADMIN_PASS`）
- 未认证请求返回 401
- 只读端点（GET /api/products、GET /api/categories）保持公开

**预估**：1-2 小时

---

### P2-4：部署自动化

- [ ] **待完成**

**改什么**：创建 `deploy.sh`（Linux）和 `nginx.conf` 模板，按照 SEM 方案第八章的架构。

**为什么**：方案描述了一个干净的 Nginx + FastAPI 部署架构，但未实现。没有部署脚本，每次上线都是手工操作且容易出错。

**验收标准**：
- `deploy.sh` 脚本：git pull -> pip install -> python build.py -> 重启 FastAPI 服务
- `nginx.conf` 模板：80->443 重定向、Let's Encrypt 路径、静态文件服务 + API 反代
- `systemd` 服务文件模板（`motor-api.service`）
- DEVELOPMENT.md 中更新部署说明

**预估**：2-3 小时

---

## 🔵 P3 — 后期迭代（锦上添花）

### P3-1：Playwright 端到端测试

- [ ] **待完成**

**改什么**：添加 Playwright 进行视觉回归和关键路径测试。项目已安装 Playwright（`package.json` 中有），但零测试。

**为什么**：网站通过 build.py 构建，有许多动态生成的内容（产品卡片、详情页）。手动测试每次改动都很耗时。

**验收标准**：
- `tests/` 目录包含：
  - `homepage.spec.js` — 轮播导航、统计数据动画、表单提交
  - `products.spec.js` — 侧边栏 Tab 切换、卡片渲染、搜索
  - `product-detail.spec.js` — 图片浏览、规格表展示
- `npx playwright test` 全部通过

**预估**：1 天

---

### P3-2：结构化错误处理和日志

- [ ] **待完成**

**改什么**：将裸 `print()` 语句替换为 Python `logging` 模块。为 FastAPI 异常添加适当的错误响应。

**为什么**：当前 `serve.py` 和 `backend/` 都使用 `print()` 进行所有输出。在无头生产环境中，日志会丢失。当 API 调用失败时，客户端得到的错误信息极少。

**验收标准**：
- backend/ 中所有 Python 文件使用 `logging` 而非 `print()`
- 日志输出到 stdout 并支持通过环境变量设置级别
- API 错误返回 `{"error": "具体消息"}` JSON 而非通用字符串
- 邮件发送失败被记录但不会导致请求崩溃

**预估**：2-3 小时

---

### P3-3：数据备份机制

- [ ] **待完成**

**改什么**：创建定时备份 `data/products.json`、`data/categories.json` 和 MySQL 数据库的脚本。DEVELOPMENT.md P3 #14。

**为什么**：产品数据是业务核心。管理后台的误操作会瞬间删除产品。需要自动备份。

**验收标准**：
- `scripts/backup.sh`：将 products.json + categories.json + audit.json + MySQL dump 打包为带时间戳的 tar.gz
- 可通过 cron 运行（每日/每周）
- 备份文件保存到 `backups/` 目录（已加入 .gitignore）

**预估**：1 小时

---

## 改进后的项目结构（目标状态）

```
HCSweb/
├── requirements.txt               # 🆕 Python 依赖
├── build.py
├── AGENTS.md                      # 随进展保持更新
│
├── index.html
├── products.html
├── product-detail-template.html
├── other-motor.html
├── throttle-motor.html
├── turbo-motor.html
├── 404.html                       # 🆕 错误页面
│
├── inc/                           # HTML 组件片段
├── css/                           # 样式（内联）
├── js/
│   ├── common.js
│   ├── nav-search.js
│   ├── sidebar.js
│   ├── product-detail.js
│   └── track.js                   # 🆕 广告追踪（P1-1）
│
├── landing/                       # 🆕 SEM 落地页（P1-1）
│   ├── micro-switch.html
│   ├── throttle-motor.html
│   ├── egr-motor.html
│   ├── epb-motor.html
│   └── turbo-motor.html
│
├── data/
│   ├── products.json              # 随进展扩展（P1-3）
│   ├── categories.json
│   └── audit.json
│
├── images/ + fonts/
├── dist/                          # 构建输出
│   └── landing/                   # 🆕（P1-1）
│
├── backend/                       # 统一后端（P0-2）
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── admin.html
│   ├── routes/
│   │   ├── products.py
│   │   └── leads.py               # 🆕 线索 API（P1-1）
│   └── uploads/
│
├── tests/                         # 🆕 Playwright 测试（P3-1）
├── scripts/
│   └── backup.sh                  # 🆕（P3-3）
├── deploy.sh                      # 🆕（P2-4）
├── nginx.conf                     # 🆕（P2-4）
├── motor-api.service              # 🆕（P2-4）
│
└── docs/
    ├── DEVELOPMENT.md
    ├── IMPROVEMENT-PLAN.md        # 本文件
    ├── claude-memory/
    └── superpowers/
        ├── plans/
        └── specs/
```

---

## AI 代理快速启动

如果本文件由新的 AI 代理在新电脑上打开：

```bash
# 1. 设置 Python 环境
python --version          # 需要 3.10+
pip install -r requirements.txt

# 2. 配置 MySQL（如不可用则跳过，仅静态站点也能工作）
#    编辑 backend/config.py 设置数据库凭据

# 3. 构建站点
PYTHONIOENCODING=utf-8 python build.py

# 4. 启动开发服务器
PYTHONIOENCODING=utf-8 python backend/main.py
#    或用于快速静态预览：
#    cd dist && PYTHONIOENCODING=utf-8 python -m http.server 8080 --bind 0.0.0.0

# 5. 打开浏览器访问 http://localhost:8000（FastAPI）或 http://localhost:8080（静态）
```
---

## 📋 评审意见（2026-06-11）

> 基于项目实际情况的逐项评估。**原计划全部保留**，本评审提供对比视角和修正建议。

---

### 总体判断

| | 原计划 | 评审建议 |
|------|--------|----------|
| 预估总工时 | 5-8 天 | 4-6 天（去掉了过度工程化的部分） |
| 技术路线 | FastAPI + MySQL 统一后端 | **保留 JSON + serve.py**，100 个产品以内够用 |
| 最大风险 | 低估了内容填充的业务依赖 | 同左，P0-5 和 P1-3 需要业务方提供素材 |

**核心分歧**：原计划假设 MySQL 是必要的，评审认为 **JSON 文件在 <100 产品场景下完全够用**。引入 MySQL 的唯一理由是防止同行直接下载 `products.json`——这个问题有更简单的解法。

---

### 逐项评审

#### P0-1：添加 requirements.txt ✅ 原计划合理

| 原计划 | 评审 |
|--------|------|
| 15 分钟，创建 requirements.txt | **同意。** 换了电脑 `pip install -r requirements.txt` 一键搞定。实际文件应包括：`fastapi`、`uvicorn`、`pymysql`、`pydantic`。 |

➡️ **执行**：照原计划做。

---

#### P0-2：合并双后端到 FastAPI ⚠️ 路线需修正

| 原计划 | 评审 |
|--------|------|
| 1-2 天，serve.py 全部功能迁到 FastAPI + MySQL | **不同意一次性迁移。** 实际产品 <100 个，JSON 文件性能完全够用。引入 MySQL 带来的运维负担（服务器装数据库、配置连接、日常备份）超出收益。 |

**关键背景**：用户引入 MySQL 的动机不是高并发，而是**防止同行直接访问 `dist/data/products.json` 扒走产品目录**。这个问题不需要 MySQL 也能解决。

**修正方案**：

| 步骤 | 做什么 | 耗时 |
|------|--------|------|
| **第一步（立即）** | 去掉 `serve.py` 中 `regenerate_js()` 复制 products.json 到 dist 的逻辑，删除 `dist/data/products.json` | 15 分钟 |
| **第二步（立即）** | `/api/products` 端点加简单 token 或 referer 校验，防止批量抓取 | 30 分钟 |
| **第三步（后续）** | 等 SEM 系统（P1-1）需要线索存储时，再评估是否需要引入数据库 | 另行评估 |

➡️ **执行**：采用修正方案，暂不迁移到 MySQL。产品数超过 100 或需要复杂查询时再评估。

---

#### P0-3：移除硬编码 Windows 路径 ✅ 原计划合理

| 原计划 | 评审 |
|--------|------|
| 5 分钟，改 `ADMIN_HTML` 为相对路径 | **同意。** 但原计划漏了一个事实：`serve.py` 里 `ADMIN_DIR = os.path.join(BASE_DIR, 'backend')` 已经是相对路径，这点 serve.py 比 backend/main.py 做得好。 |

➡️ **执行**：照原计划做，同时确认 serve.py 无其他硬编码路径。

---

#### P0-4：删除死代码 ✅ 原计划合理

| 原计划 | 评审 |
|--------|------|
| 10 分钟，删 `static-server.js`、`nav.html.bak` | **同意。** 无害但让新来的 AI 困惑。附加：`package.json` 的 `"main": "static-server.js"` 也需更新。 |

➡️ **执行**：照原计划做。

---

#### P0-5：首页内容填充 ⚠️ 时间需修正

| 原计划 | 评审 |
|--------|------|
| 2-4 小时 | **时间太乐观。** 新闻内容、产品图片需要业务方提供素材，不是纯编码工作。六边形产品图相对好办（从 `images/products/` 取），但新闻板块如果没有素材，建议先隐藏。 |

➡️ **执行**：六边形部分可独立完成（1 小时），新闻和关于我们图片需等待素材。

---

#### P0-6：移动端适配 ✅ 原计划合理

| 原计划 | 评审 |
|--------|------|
| 4-6 小时，375px 宽度全面审核 | **同意。** 国内 B2B 客户手机浏览占比高，移动端溢出和重叠问题确实存在。 |

➡️ **执行**：照原计划做。

---

#### P1-1：SEM 营销系统 ✅ 原计划合理，但数据存储方案需调整

| 原计划 | 评审 |
|--------|------|
| 3 天，track.js + landing/ + leads API + MySQL | **同意方向和工时。** 但 leads 表不一定要 MySQL——考虑到产品数据短期内也用 JSON，线索数据可以先用 JSON 文件存储，后续量大再迁数据库。这样 P1-1 完全不依赖 P0-2。 |

**具体调整**：

| 原计划 | 调整后 |
|--------|--------|
| `backend/routes/leads.py` + MySQL `leads` 表 | `serve.py` 新增 `POST /api/lead`，线索写入 `data/leads.json` |
| 管理后台需要 MySQL 连接 | 管理后台读 `data/leads.json` 展示线索列表 |
| leads 表 SQL schema | 保留作为参考，字段设计不变，存储从 MySQL 改为 JSON |

➡️ **执行**：track.js 和 landing/ 照原计划，线索存储先用 JSON。日访问量上来后再迁 MySQL。

---

#### P1-2：SEO 基础优化 ✅ 原计划合理

| 原计划 | 评审 |
|--------|------|
| 3-4 小时，TDK + sitemap + 结构化数据 + alt | **同意。** 竞品都不做 SEO，这是低成本高回报的事。 |

➡️ **执行**：照原计划做。

---

#### P1-3：添加更多产品数据 ✅ 原计划合理

| 原计划 | 评审 |
|--------|------|
| 4-8 小时，扩充到覆盖所有子类目 | **同意方向。** 但和 P0-5 一样，需要业务方提供产品信息。微动开关产品是 SEM 落地页的硬依赖，优先级最高。 |

➡️ **执行**：优先准备微动开关产品（主力落地页需要），其他子类目按需补充。

---

#### P2-1：全站字号加大 ✅ 原计划合理

| 原计划 | 评审 |
|--------|------|
| 1-2 小时，正文基线 +1~2px | **同意。** 客户群体偏年长（工业采购决策者），Share Tech Mono 在小字号下尤其难读。改 `common.css` 的 CSS 变量即可。 |

➡️ **执行**：照原计划做。

---

#### P2-2：404 错误页面 ✅ 原计划合理

| 原计划 | 评审 |
|--------|------|
| 30 分钟，品牌化 404 页 | **同意。** 删了产品后旧链接需要友好降级。 |

➡️ **执行**：照原计划做。

---

#### P2-3：管理后台安全加固 ✅ 原计划合理

| 原计划 | 评审 |
|--------|------|
| 1-2 小时，HTTP Basic Auth | **同意。** 上线前必须加。用环境变量配置用户名密码，不需要数据库。 |

➡️ **执行**：照原计划做。

---

#### P2-4：部署自动化 ⚠️ 时机过早

| 原计划 | 评审 |
|--------|------|
| 2-3 小时，deploy.sh + nginx.conf + systemd | **取决于部署目标。** 目前还没确定部署到哪（云服务器？虚拟主机？），提前写 nginx.conf 可能白写。建议等部署环境确定后再做。 |

➡️ **执行**：延期到部署环境确定后。

---

#### P3-1：Playwright E2E 测试 ❌ 不推荐

| 原计划 | 评审 |
|--------|------|
| 1 天，端到端测试 | **过度工程化。** 对静态 HTML 网站引入 E2E 测试框架，投入产出比极低。手动打开浏览器点一遍各页面 + 产品详情页，5 分钟搞定。 |

➡️ **执行**：**跳過**。产品数 >50 或引入复杂交互后再考虑。

---

#### P3-2：日志规范化 △ 低优先级

| 原计划 | 评审 |
|--------|------|
| 2-3 小时，print() → logging | **做了更好，不做也行。** serve.py 的 print 输出在生产环境确实会丢，但目前运维靠人工看终端，logging 模块的紧迫性不高。 |

➡️ **执行**：**延期**。等 P2-4 部署自动化时一起做。

---

#### P3-3：数据备份 ✅ 原计划合理

| 原计划 | 评审 |
|--------|------|
| 1 小时，备份脚本 | **同意。** 管理后台的误删操作可能瞬间丢失产品数据。JSON 文件的备份比 MySQL 更简单——直接 tar 打包即可。 |

➡️ **执行**：照原计划做。

---

### 修正后的推荐执行顺序

```
第一波（半天，上线前）：
  ├── P0-3  去硬编码路径（5 分钟）
  ├── P0-4  删死代码（10 分钟）
  ├── 🆕    堵 products.json 泄露（30 分钟）
  ├── P2-2  404 页面（30 分钟）
  └── P2-1  字号加大（1 小时）

第二波（半天，上线前）：
  ├── P2-3  管理后台加认证（1 小时）
  ├── P0-5  首页六边形填充（1 小时，新闻板块等素材）
  └── P0-6  移动端适配（4 小时）

第三波（3-4 天，上线后）：
  ├── P1-1  SEM 营销系统（track.js + landing/ + 线索 API，先用 JSON 存储）
  ├── P1-2  SEO 优化
  └── P1-3  补充产品数据（微动开关优先）

第四波（按需）：
  ├── P3-3  数据备份
  ├── P2-4  部署自动化（等部署环境确定）
  └── P3-2  日志规范化（等部署自动化时一起做）

不推荐做：
  ├── P3-1  Playwright 测试（跳过）
  └── P0-2  完整 MySQL 迁移（延期到产品 >100 或需要复杂查询时）
```

---

### 评审总结

| 原计划 | 评审建议 |
|--------|----------|
| 16 项改进 | 14 项保留，1 项跳过（P3-1），1 项路线修正（P0-2），2 项延期（P2-4、P3-2） |
| 新增 1 项：**堵 products.json 泄露**（30 分钟） | |
| 预估总工时从 5-8 天降到 **4-6 天** | |
| JSON 优先，MySQL 等产品 >100 或业务需要时再评估 | |
---

## 📋 Codex 复核（2026-06-11）

> 对评审意见的逐条反馈。**与评审的共识和分歧均列在下表**，分歧项给出修正建议。

---

### 总体判断：评审方向正确

| 评审结论 | 复核 |
|----------|------|
| JSON 优先，MySQL 延期 | ✅ 同意。100 产品以内 JSON 无性能问题，运维负担为零 |
| 新增"堵 products.json 泄露" | ✅ 同意。原计划遗漏了这个安全漏洞 |
| P3-1 Playwright 跳过 | ✅ 同意。静态 HTML 网站引入 E2E 过度工程化 |
| P2-4 部署自动化延期 | ✅ 同意。无目标环境时写 nginx.conf 是猜测 |
| P0-5/P1-3 工时需业务配合 | ✅ 同意。内容填充不是纯编码工作 |

---

### ⚠️ 分歧 #1：评审未明确 `backend/` 目录的去留

**问题**：评审将 P1-1（线索 API）调整为进 `serve.py` + JSON，P0-2（MySQL 迁移）延期——但没有说明 `backend/` 目录怎么处理。当前状态：

```
serve.py          ← 实际在用，产品CRUD + contact + 分类 + 图片上传 + admin
backend/main.py   ← FastAPI，功能子集，硬编码路径，未被日常使用
```

如果只增加不清理，serve.py 继续膨胀（新增 leads API），backend/ 闲置且有安全隐患（`config.py` 空密码、`main.py` 硬编码路径）。新人打开项目会困惑"两个后端到底用哪个"。

**建议修正**：在评审的 P0-2 结论后追加一句：

> `serve.py` 作为唯一后端。`backend/` 目录保留作代码参考（pymysql 封装和 FastAPI 路由写得干净，将来如果真需要数据库迁移可直接复用），但 `AGENTS.md` 中标注 backend/ 为"保留参考，暂不使用，不参与当前开发流程"。

同时更新 `AGENTS.md` 的 Key project areas，为 backend/ 条目加一行 `**当前状态：保留参考，暂不使用。**`

---

### ⚠️ 分歧 #2：P0-3 与 P0-2 联动降级

**问题**：评审建议 P0-2 延期，但 P0-3（移除硬编码路径）改动的是 `backend/main.py`。如果 `backend/` 暂不使用，P0-3 的价值需要重新评估——改一个暂不使用的文件，优先级应该降低。

**建议修正**：P0-3 从 P0 降级到 P2，或直接在 P0-3 条目里追加一行：

> 如果 backend/ 暂不使用（见 P0-2 评审修正），此条可降为最低优先级。改它只是为了将来复用时代码整洁。

---

### ⚠️ 分歧 #3：P1-1 落地页构建缺少样式复用提醒

**问题**：评审保留了 P1-1（SEM 系统），但 SEM 方案第四章要求落地页"品牌延续——深色底 + 青/金/粉配色 + 自托管 Orbitron/Share Tech Mono 字体"。如果 P1-1 实施时忽略了这一点，落地页可能会写一套独立样式，导致：

- 改一处配色需要改两个地方（主站 + landing/）
- 落地页和主站视觉不一致

**建议修正**：在评审的 P1-1 具体调整表里追加一行：

| 原计划 | 调整后 |
|--------|--------|
| 落地页独立 CSS | `landing/` 页面复用 `<!-- #include css:common -->` 获取 CSS 变量和基础样式。在 `build.py` 的 `CSS_MAP` 里新增 `landing` 键指向 `landing.css`（仅放落地页特有样式，不超过 100 行） |

---

### ✅ 完全同意的部分（无需修改）

| 条目 | 评审意见 | 理由 |
|------|---------|------|
| P0-1 requirements.txt | 同意，照做 | 换了电脑能一键装依赖，投入产出最高 |
| P0-4 删死代码 | 同意，照做 | 10 分钟消除新人困惑 |
| P0-6 移动端适配 | 同意，照做 | B2B 客户手机浏览占比高 |
| P1-2 SEO 优化 | 同意，照做 | 竞品都不做，低成本高回报 |
| P2-1 字号加大 | 同意，照做 | 客户群体偏年长 |
| P2-2 404 页面 | 同意，照做 | 删除产品后旧链接需要友好降级 |
| P2-3 管理后台认证 | 同意，照做 | 上线前必须加 |
| P3-3 数据备份 | 同意，照做 | JSON 文件备份比 MySQL 更简单 |

---

### 复核结论

| 维度 | 评审 | 复核 | 最终建议 |
|------|------|------|----------|
| 技术路线 | serve.py + JSON | ✅ 同意 | serve.py 唯一后端，backend/ 保留参考 |
| 总工时 | 4-6 天 | ✅ 同意 | 合理 |
| 遗漏项 | 无 | 3 个 | 见分歧 #1/#2/#3 |
| 需修改条目 | 无 | P0-3 降优先级 | 改暂不使用的文件不必 P0 |

> 评审整体质量高。三个分歧都是细节补充，不改变总体路线。关键是明确 backend/ 的处置，避免双后端状态在文档里也持续模糊。
---

## 📋 最终综合结论（2026-06-11）

> 原计划 → 评审意见 → Codex 复核，三层叠加后的最终共识。

---

### 三层观点演变

| 条目 | 原计划 | 评审 | Codex 复核 | **最终** |
|------|--------|------|-----------|----------|
| P0-1 requirements.txt | ✅ P0,15min | 同意 | 同意 | **照做** |
| P0-2 合并后端 | P0,1-2天,→MySQL | ⚠️ 延期,JSON优先 | +追加:backend/保留参考 | **延期。serve.py唯一后端，backend/保留参考** |
| P0-3 去硬编码路径 | P0,5min | 同意 | ⚠️ 降级(backend/暂不用) | **降为P2。改backend/main.py等复用时再做** |
| P0-4 删死代码 | P0,10min | 同意 | 同意 | **照做** |
| 🆕 堵products.json泄露 | 未提及 | P0新增,30min | **补充方案选型分析** | **P0新增，选定频率限制方案** |
| P0-5 首页填充 | P0,2-4h | ⚠️ 工时需素材 | 同意 | **六边形1h可做，新闻等素材** |
| P0-6 移动端适配 | P0,4-6h | 同意 | 同意 | **照做** |
| P1-1 SEM系统 | P1,3d,MySQL | ⚠️ 改JSON存储 | +追加:落地页复用common.css | **照做，线索JSON存储，落地页复用CSS变量** |
| P1-2 SEO优化 | P1,3-4h | 同意 | 同意 | **照做** |
| P1-3 扩充产品 | P1,4-8h | ⚠️ 微动开关优先 | 同意 | **微动开关优先，其他按需** |
| P2-1 字号加大 | P2,1-2h | 同意 | 同意 | **照做** |
| P2-2 404页面 | P2,30min | 同意 | 同意 | **照做** |
| P2-3 管理后台认证 | P2,1-2h | 同意 | 同意 | **照做** |
| P2-4 部署自动化 | P2,2-3h | ⚠️ 延期 | 同意 | **延期到部署环境确定** |
| P3-1 Playwright测试 | P3,1d | ❌ 跳过 | 同意 | **跳过** |
| P3-2 日志规范化 | P3,2-3h | △ 延期 | 同意 | **延期，等部署自动化时一起做** |
| P3-3 数据备份 | P3,1h | 同意 | 同意 | **照做** |

---

### 🆕 堵 products.json 泄露（补充验收标准 + 方案选型分析）

- [ ] **待完成**

**改什么**：防止同行通过静态 URL 直接下载完整产品数据，以及通过 API 批量抓取。

**为什么**：`serve.py` 的 `regenerate_js()` 会将完整产品数据复制到 `dist/data/products.json`，任何人访问 `/data/products.json` 即可获取全部产品目录。同时 `/api/products` 无任何访问控制，可被脚本批量抓取。`products.js` 存在相同泄漏风险（同数据，不同格式，当前也未正确部署到 dist/）。

**验收标准**：
- `dist/data/products.json` 文件不存在（`regenerate_js()` 不再向 dist 写入产品 JSON）
- `dist/data/products.js` 文件不存在（`products.js` 数据改为构建时内联注入 HTML，不再以静态文件方式暴露在 dist/ 中）
- `/api/products` 添加同 IP 频率限制：同一 IP 每分钟超过 10 次请求返回 429
- `/api/search` 添加同 IP 频率限制：同一 IP 每分钟超过 10 次请求返回 429
- Fuse.js 前端搜索仍正常工作（build.py 处理 `<!-- #include js:nav-search -->` 时将 products.js 的 `PRODUCTS_DATA` 数组内联到 `<script>` 标签中，替代原有 `<script src="data/products.js">` 外链）
- 管理后台 /admin 的产品 CRUD 操作不受频率限制影响（走 serve.py 内部逻辑，不经过限速）
- 验证：运行 build.py + serve.py 后，浏览器访问 `/data/products.json` 和 `/data/products.js` 均返回 404

**预估**：1 小时（含 products.js 内联改造）

---

### 堵漏方案选型分析

> 验收标准选定了"频率限制"，以下是为什么没选 token 和 Referer。

**评估维度**：① 防范同行脚本扒数据的能力 ② 页面响应速度开销 ③ 实现成本

| 维度 | URL Token | Referer 白名单 | **频率限制（选定）** |
|------|-----------|---------------|---------------------|
| 防脚本直接下载 `/api/products` | ✅ 彻底阻断（脚本不知道 token） | ❌ 一行代码绕过（Referer 可任意伪造） | ⚠️ 拖慢到不值得爬（同 IP 限 10 次/分钟，300 产品需半小时） |
| 防脚本伪造身份 | ✅ token 不在公开页面里 | ❌ header 可伪造，无身份校验意义 | ✅ 按 IP 限速，不依赖身份 |
| 需改 admin.html | ✅ 每个 fetch 都要拼 `?token=` | ❌ 不改 | ❌ 不改 |
| 单次请求额外耗时 | <0.1ms（字符串比较） | <0.1ms | <0.5ms（内存哈希表：获取 IP → 清理过期时间戳 → 计数） |
| 对正常用户可见延迟 | 0 | 0 | 0（正常用户不会一分钟点 10 次） |
| 内存占用 | 0 | 0 | <50KB（假设 100 个并发 IP × 10 个时间戳） |

**Referer 为什么淘汰**：Referer 的原始设计目的是防盗链（阻止别人 `<img src>` 蹭带宽），不是访问控制。脚本加一行 `headers={"Referer": "https://hcsmotor.cn/"}` 就能绕过。挡不住同行。

**Token vs 频率限制**：两者不互斥，解决不同层面的问题——token 管"你是谁"，频率限制管"你有多快"。对于"防同行扒数据"，频率限制就够了，因为同行的目的是批量获取。频率限制正好打在批量上。

**为什么没选 Token**：Token 能提供更强保护，但代价是 admin.html 里每个 fetch 都要拼 `?token=`，实现成本高。当前产品 <100 个、威胁等级下（竞品不会专门搭代理池来爬），频率限制投入产出比最高。将来产品数增长、竞品开始用代理池爬数据时，再叠加 token 不迟（两方案不互斥）。

**频率限制实现要点**（供实施参考）：

```python
# serve.py 中维护内存字典：
# { "192.168.1.1": [timestamp, timestamp, ...] }
# 每次请求：清理超过 60 秒的时间戳 → 计数 → 超过 10 个返回 429
# 内存开销：100 个并发 IP × 10 个 int × 8 字节 ≈ 8KB
# serve.py 单进程，无需考虑分布式限速
```

---

### 最终执行顺序

```
第一波（2小时，立刻做）：
  ├── P0-3  去硬编码路径 → 降为P2，只做 serve.py 侧（已是相对路径，确认即可）
  ├── P0-4  删死代码（10 分钟）
  ├── 🆕    堵 products.json 泄露（1 小时）
  ├── P2-2  404 页面（30 分钟）
  └── P2-1  字号加大（1 小时）

第二波（6小时，上线前）：
  ├── P2-3  管理后台加认证（1 小时）
  ├── P0-5  首页六边形填充（1 小时，新闻等素材）
  └── P0-6  移动端适配（4 小时）

第三波（3-4天，上线后）：
  ├── P1-1  SEM营销系统（track.js + landing/ + leads JSON API）
  │         └── 落地页复用 <!-- #include css:common --> 获取CSS变量
  │         └── 线索存入 data/leads.json，不引入MySQL
  ├── P1-2  SEO优化
  └── P1-3  补充产品数据（微动开关优先）

第四波（按需触发）：
  ├── P3-3  数据备份（1小时）
  ├── P2-4  部署自动化（等部署环境确定）
  ├── P3-2  日志规范化（等部署自动化时一起做）
  └── P0-3  去backend/硬编码路径（等将来复用backend/时再做）

不推荐做：
  ├── P3-1  Playwright测试
  └── P0-2  完整MySQL迁移（产品>100或需复杂查询时再评估）
```

---

### backend/ 目录处置

```
backend/  当前状态：保留参考，暂不使用
  ├── main.py / routes/products.py  → 干净的FastAPI参考实现，将来需要时可复用
  ├── database.py                   → pymysql封装，迁移数据库时直接可用
  ├── config.py                     → ⚠️ 含空MySQL密码，不要部署到公网
  └── admin.html                    → 管理后台页面，当前由serve.py服务

serve.py   当前唯一后端
  ├── 产品CRUD（JSON文件）
  ├── 联系表单 + SMTP
  ├── 图片上传
  ├── 分类管理
  ├── /admin 管理后台
  ├── 搜索API
  ├── 审计日志
  └── 自动构建
```

> 对应的 AGENTS.md 更新：在 backend/ 条目下追加 `**当前状态：保留参考，暂不使用。日常开发走 serve.py。**`

---

### 综合结论

| 维度 | 最终状态 |
|------|----------|
| 改进项 | 原16项 + 新增1项（堵漏）= 17项 |
| 照做 | 10项（P0-1/4/5/6, P1-1/2/3, P2-1/2/3, P3-3） |
| 修正路线 | 1项（P0-2：MySQL延期，JSON优先，backend/保留参考） |
| 降级 | 1项（P0-3：P0→P2，只做serve.py侧确认） |
| 延期 | 2项（P2-4, P3-2） |
| 跳过 | 1项（P3-1） |
| 总工时 | **5-7天**（比评审的4-6天多了1天，含堵漏products.js内联 + 落地页样式复用 + backend处置） |
| 技术路线 | **serve.py + JSON 唯一后端**，MySQL 等产品 >100 或业务需要 |
| 下一个行动 | 执行第一波：P0-4 → 堵漏 → P2-2 → P2-1 |

---

## 维护本文件

与其他项目文档相同的规则：完成一个改进项后，将 `[ ]` 改为 `[x]`。将新发现添加到对应优先级板块。本文件是活的。

> 基线评估日期：2026-06-11
> 评审日期：2026-06-11
> 评估摘要：组件化重构扎实。主要差距 = 双后端未整合、SEM 系统未实施、内容为占位数据、无依赖管理。预估整合和上线工作量为 4-6 天。
> 评审修正：JSON 优先策略，MySQL 延期；新增数据泄露堵漏项；Playwright 测试跳过。
> Codex复核补全：堵漏验收标准细化 + 方案选型分析（频率限制 vs Token vs Referer）；backend/ 处置结论；P0-3 联动降级。