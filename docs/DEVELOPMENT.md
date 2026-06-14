# DEVELOPMENT.md — 华创生电机官网开发文档

> **用途**：换电脑后用 Claude Code 打开项目时，读取本文档即可无缝衔接开发。
> **维护规则**：架构变化和约定更新到本文档。开发工作记录和踩坑追加到 [DEVLOG.md](DEVLOG.md)。本文档是活的，不是一次性的。

---

## 一、项目概述

华创生电机（HCS Motor）企业官网，德昌电机（JOHNSON ELECTRIC）授权代理商。

- **类型**：静态 HTML 网站 + 轻量后端
- **前端**：原生 HTML/CSS/JS，无框架，赛博朋克暗色主题（Orbitron + Share Tech Mono 字体）
- **构建**：Python `build.py` 将共享组件（nav/sidebar/footer）内联注入 HTML，CSS/JS 也内联化，输出到 `dist/`
- **开发服务器**：`serve.py`（Python HTTP 服务器，含表单/产品/分类/搜索 API，JSON 文件存储）
- **后端 API（保留参考）**：FastAPI（`backend/main.py`，含产品 CRUD、MySQL 数据库），**当前暂不使用**
- **部署目标**：静态站点（`dist/` 目录）+ serve.py 后端（Nginx 反代）
- **历史记录**：已完成的开发工作和踩坑见 [DEVLOG.md](DEVLOG.md)

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

> **历史工作记录**：已完成的开发工作和踩坑记录移至 [DEVLOG.md](DEVLOG.md)。ARCHIVE.md 记录已废弃的功能。

---

## 五、开发约定

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

## 六、待办事项

### 🔴 P0 — 上线前
1. 网站部署（见 [第七章·部署方案](#七部署方案)）：确认服务器 → 环境安装 → 代码部署 → Nginx 配置 → 上线
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

## 七、部署方案

> **当前状态**：域名 `hcsmotor.cn` 已解析到阿里云轻量应用服务器，HTTPS 已配置。原万网智能建站模板需要替换为 HCSweb 项目代码。
> **目标**：将 HCSweb 项目部署上线，包含静态站点 + FastAPI 后端 + MySQL。

### 10.1 服务器选型

**推荐：阿里云轻量应用服务器（2核2G，¥612/年）**

| 组件 | 方案 |
|------|------|
| 系统镜像 | Ubuntu 22.04 / 24.04 |
| 应用镜像 | 可选 "Node.js / Python" 预装镜像 |
| Web 服务器 | Nginx（静态文件 + 反向代理） |
| 应用服务 | FastAPI（uvicorn，systemd 守护） |
| 数据库 | MySQL 8.0（同机安装） |
| SSL | Let's Encrypt（certbot 自动续期） |

> 不选虚拟主机：跑不了 Python。不选 ECS：过度配置，轻量服务器够用。

### 10.2 环境安装

```bash
# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装 Nginx
sudo apt install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx

# 3. 安装 Python 3
sudo apt install python3 python3-pip -y

# 4. 安装 MySQL 8.0
sudo apt install mysql-server -y
sudo systemctl enable mysql
sudo systemctl start mysql

# 5. 初始化 MySQL
sudo mysql_secure_installation
# 按提示设置 root 密码，移除匿名用户，禁止远程 root

# 6. 创建数据库
sudo mysql -u root -p << EOF
CREATE DATABASE IF NOT EXISTS motor_website DEFAULT CHARACTER SET utf8mb4;
CREATE USER IF NOT EXISTS 'motor'@'localhost' IDENTIFIED BY '<你的密码>';
GRANT ALL PRIVILEGES ON motor_website.* TO 'motor'@'localhost';
FLUSH PRIVILEGES;
EOF

# 7. 安装 Python 依赖
sudo pip3 install fastapi uvicorn pymysql
# 或使用 requirements.txt（待创建）

# 8. 安装 certbot（SSL 证书）
sudo apt install certbot python3-certbot-nginx -y
```

### 10.3 部署代码

```bash
# 1. 克隆项目
cd /var/www
sudo git clone https://github.com/yangjian19930109/HCSweb.git hcsmotor
sudo chown -R $USER:$USER /var/www/hcsmotor

# 2. 配置后端数据库连接
# 编辑 backend/config.py，修改 MySQL 密码为实际密码

# 3. 构建静态文件
cd /var/www/hcsmotor
PYTHONIOENCODING=utf-8 python3 build.py

# 4. 创建上传目录
mkdir -p /var/www/hcsmotor/backend/uploads
chmod 755 /var/www/hcsmotor/backend/uploads
```

### 10.4 Nginx 配置

```nginx
# /etc/nginx/sites-available/hcsmotor
server {
    listen 80;
    server_name hcsmotor.cn www.hcsmotor.cn;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name hcsmotor.cn www.hcsmotor.cn;

    # SSL（certbot 自动生成）
    ssl_certificate     /etc/letsencrypt/live/hcsmotor.cn/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/hcsmotor.cn/privkey.pem;

    # 静态文件（dist/ 目录）
    root /var/www/hcsmotor/dist;
    index index.html;

    # API 反代到 FastAPI
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 管理后台反代
    location /admin {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    # 上传文件
    location /uploads/ {
        alias /var/www/hcsmotor/backend/uploads/;
    }

    # 静态文件缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff2?|ttf|svg)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # SPA fallback（404 → index.html）
    location / {
        try_files $uri $uri/ $uri.html /index.html;
    }
}
```

启用配置：

```bash
sudo ln -sf /etc/nginx/sites-available/hcsmotor /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# SSL 证书申请
sudo certbot --nginx -d hcsmotor.cn -d www.hcsmotor.cn
```

### 10.5 FastAPI 服务管理

```ini
# /etc/systemd/system/motor-api.service
[Unit]
Description=Motor Website API
After=network.target mysql.service

[Service]
User=www-data
WorkingDirectory=/var/www/hcsmotor
ExecStart=/usr/bin/python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
Environment=PYTHONIOENCODING=utf-8

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable motor-api
sudo systemctl start motor-api
```

### 10.6 数据库表初始化

```sql
-- 产品分类表
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    sort_order INT DEFAULT 0
);

-- 产品表
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT,
    model VARCHAR(100),
    name VARCHAR(200),
    description TEXT,
    specs TEXT,
    image_url VARCHAR(500),
    file_url VARCHAR(500),
    featured BOOLEAN DEFAULT FALSE,
    sort_order INT DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- 线索表（上线后创建，暂不必须）
-- CREATE TABLE leads (...)
```

### 10.7 部署检查清单

| 检查项 | 命令 / 方法 |
|--------|-----------|
| Nginx 状态 | `sudo systemctl status nginx` |
| FastAPI 状态 | `sudo systemctl status motor-api` |
| MySQL 状态 | `sudo systemctl status mysql` |
| 静态文件 | `curl -I https://hcsmotor.cn/` → HTTP 200 |
| API 接口 | `curl https://hcsmotor.cn/api/health` → `{"status":"ok"}` |
| 管理后台 | `curl -I https://hcsmotor.cn/admin` → HTTP 200 |
| SSL 证书 | `sudo certbot certificates` |
| 端口 | `sudo netstat -tlnp \| grep -E ':(80\|443\|8000\|3306)'` |
| 构建 | `cd /var/www/hcsmotor && PYTHONIOENCODING=utf-8 python3 build.py` |

### 10.8 更新部署流程

每次代码更新后：

```bash
# 本地
git add -A && git commit -m "描述" && git push

# 服务器
cd /var/www/hcsmotor
git pull
PYTHONIOENCODING=utf-8 python3 build.py    # 重新构建 dist/
sudo systemctl restart motor-api           # 重启 API（如有更新）
# 静态文件不需要重启，Nginx 直接服务
```

### 10.9 常见问题

**Q: 轻量服务器能跑 Python + MySQL 吗？**
A: 能。2核2G 跑 FastAPI + MySQL + Nginx 足够，内存有富余。

**Q: 现有万网智能建站怎么办？**
A: 替换。Nginx 配置指向 HCSweb 的 `dist/` 目录后，原模板就不再生效。

**Q: 服务器已经在跑万网模板，Nginx 配置会冲突吗？**
A: 需要确认当前服务器环境。如果是轻量服务器 + 已有的 Nginx，直接追加配置。如果是万网托管平台（无 SSH），则需要新购轻量服务器。

---

## 八、如何更新本文档

每次完成有效的开发工作或踩坑后，把关键信息追加到对应章节：

- **新功能 / 新坑 / 经验教训** → 追加到 [DEVLOG.md](DEVLOG.md)，按日期记录
- **架构变化** → 更新第四章"核心架构"和第二章"目录结构"
- **新约定** → 更新第五章"开发约定"
- **待办变化** → 更新第六章

原则：让换一台电脑的 Claude Code 读完后，不需要重新踩你已经踩过的坑。

---

> 最后更新：2026-06-11
