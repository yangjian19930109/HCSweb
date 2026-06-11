# 执行方案

> 由 IMPROVEMENT-PLAN.md 的三层评审（原计划 → 评审 → Codex 复核 → 最终综合）提炼而成。
> 本文档是**确定的执行方案**，不再包含讨论和分歧。原文保留在 IMPROVEMENT-PLAN.md 供追溯。

---

## 技术路线（已确定）

| 决策 | 结论 |
|------|------|
| 后端 | `serve.py` 唯一后端，JSON 文件存储 |
| MySQL | **不引入**。产品 <100 个，JSON 无性能问题。待产品 >100 再评估 |
| `backend/` 目录 | **保留参考，暂不使用**。AGENTS.md 标注后即可 |
| 数据泄露 | 立即堵：`dist/data/products.json` 不再写入，`/api/products` 加 token |

---

## 执行顺序

### 第一波：立刻做（~3 小时）🔴

#### 1. 删死代码（10 分钟）

- 删除 `static-server.js`
- 删除 `inc/nav.html.bak`
- 修改 `package.json` 的 `"main"` 字段（移除或指向 serve.py）

#### 2. 堵产品数据泄露（30 分钟）

**实际状况**（代码审计确认）：

| 载体 | 位置 | 状态 |
|------|------|------|
| `products.json` | `dist/data/products.json` | 🔴 serve.py 写入，浏览器可直接访问 |
| `products.js` | `data/products.js`（git 跟踪） | 🔴 含完整 `var PRODUCTS_DATA = [...]`，git 历史持续泄露。且 confirm 了一个潜伏 bug：`regenerate_js()` 只把 `products.json` 写入 `dist/data/`，从未把 `products.js` 写入 `dist/`（见 serve.py 第 200 行 vs 第 205 行）。如果搜索仍在用 Fuse.js 客户端方案，它早就是坏的——幸好搜索已切到 `/api/search` API |
| `regenerate_js()` | `serve.py` | 🟡 死代码——无页面引用 `products.js`，但它同时维护了 JSON 泄露和 JS 泄露 |

**执行**：
- `serve.py` 删除 `regenerate_js()` 及其调用（`save_products()` 中的 `regenerate_js(products)` 调用、启动时的生成逻辑）
- `git rm --cached data/products.js` + 加入 `.gitignore`
- `serve.py` 的 `regenerate_js()` 中删除向 `dist/data/products.json` 写入的逻辑
- `/api/products` 端点加 token 校验（环境变量 `API_TOKEN`）

#### 3. 创建 404 页面（30 分钟）

- 新建 `404.html`，含导航栏 + 页脚 + 中文提示 + 返回首页链接 + 搜索框
- `build.py` 处理 404.html 的 include 占位符

#### 4. 全站字号加大（1 小时）

- `common.css` 的 `body` 字号基线 +1~2px
- 产品卡片描述 ≥14px，规格表 ≥14px，表单标签 ≥14px

#### 5. 添加 requirements.txt（15 分钟）

- 内容：`fastapi`、`uvicorn`、`pymysql`、`pydantic`

#### 6. 更新 AGENTS.md（15 分钟）

- backend/ 条目追加 `**当前状态：保留参考，暂不使用。日常开发走 serve.py。**`
- 移除 static-server.js 相关描述

---

### 第二波：上线前（~6 小时）🔴

#### 7. 管理后台加认证（1 小时）

- `/admin` + `/api/products` 写操作（POST/PUT/DELETE）加 HTTP Basic Auth
- 凭据走环境变量 `ADMIN_USER` / `ADMIN_PASS`

#### 8. 首页六边形填充（1 小时）

- 4 个六边形表情符号替换为 `images/products/` 中的实际产品图
- 每个六边形链接到对应产品页或 `products.html`
- 新闻板块和关于我们图片待素材（先隐藏或保持占位）

#### 9. 移动端适配（4 小时）

- 375px 宽度下所有页面无水平溢出、无文字重叠
- 产品卡片单列排列，联系表单按钮 ≥44px
- 确认 Banner Slide 2 磁感线 SVG 在移动端可见

---

### 第三波：上线后（3~4 天）🟡

#### 10. SEM 营销系统（3 天）

- `js/track.js`：来源解析 + 自动事件 + 点击事件 + 表单注入（~200 行，零依赖）
- `landing/` 目录：5 个落地页（micro-switch、throttle-motor、egr-motor、epb-botor、turbo-motor）
- 落地页复用 `<!-- #include css:common -->` 获取 CSS 变量和基础样式
- `serve.py` 新增 `POST /api/lead`，线索写入 `data/leads.json`
- 管理后台新增线索列表 Tab（读 `data/leads.json`）
- `build.py` 扩展支持 landing/ 目录构建
- 百度统计 + 百度商桥代码注入 `inc/footer.html`

#### 11. SEO 基础优化（4 小时）

- 每页唯一 TDK + sitemap.xml + 图片 alt + JSON-LD 结构化数据

#### 12. 补充产品数据（依赖业务方提供素材）

- 优先：微动开关产品（SEM 主力落地页需要）
- 其次：家用电器及电动工具马达产品

---

### 第四波：按需触发 🔵

| 项目 | 触发条件 | 预估 |
|------|---------|------|
| 数据备份脚本 | 管理后台开始日常使用 | 1 小时 |
| 部署自动化 | 部署环境确定后 | 2 小时 |
| 日志规范化 | 和部署自动化一起做 | 2 小时 |
| 修复 backend/main.py 硬编码路径 | 将来决定复用 backend/ 时 | 5 分钟 |

---

### 不做

| 项目 | 理由 |
|------|------|
| Playwright E2E 测试 | 静态 HTML 网站，手动点击即可 |
| MySQL 迁移 | 产品 <100 时 JSON 完全够用 |

---

## 汇总

| 阶段 | 项目数 | 工时 |
|------|--------|------|
| 第一波（立刻） | 6 | 3 小时 |
| 第二波（上线前） | 3 | 6 小时 |
| 第三波（上线后） | 3 | 3~4 天 |
| 第四波（按需） | 3 | 4 小时 |
| **合计** | **15 项** | **5~7 天** |

---

> 制定日期：2026-06-11
> 来源：[IMPROVEMENT-PLAN.md](/docs/IMPROVEMENT-PLAN.md) — 原文保留三层评审过程供追溯
