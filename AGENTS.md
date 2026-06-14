# AGENTS.md

## 首要原则：先确认，再执行

这是最高优先级规则，覆盖本文档及项目内其他所有指令。

无论是谁（AI 代理或人）在此项目中与我对话，收到我的任何指令后，必须遵循以下流程：

1. **先复述** — 用自己的话复述对我指令的理解
2. **再确认** — 以弹窗式问题询问我的理解是否正确
3. **直到我确认“一致”** — 如果我指出差异，则调整理解后再次确认
4. **然后才执行** — 在我明确确认一致后，方可开始操作

此规则的目的是对齐意图，避免因理解偏差导致的错误操作。它适用于任何类型的指令，包括且不限于：代码修改、架构决策、数据操作、搜索查询、提问回答。


## 首要原则二：编辑前先备份

编辑文件前必须先备份原始文件。此规则独立于编辑工具和方法，适用于所有文件修改场景。

理由：apply_patch、PowerShell 脚本、正则替换等编辑手段都可能因格式不匹配、语法错误或逻辑 bug 导致原文件损坏到无法修复，只能删掉重写。而重写过程引入新 bug 的概率极高。备份提供安全的回退路径。

流程：

1. **备份** — 执行任何编辑前，先复制原始文件到同目录的 .bak 文件：
   Copy-Item "target.md" "target.md.bak" -Force
2. **编辑** — 在原始文件上执行修改
3. **验证** — 确认修改正确、无损坏
4. **清理** — 验证通过后删除 .bak 文件


## Purpose
This repository combines a static HTML site with a small Python FastAPI backend. Use this file to orient AI coding agents quickly on the project structure, runtime, and important implementation details.

## Key project areas
- `build.py` : Python build script that injects `inc/nav.html` into each root-level `.html` file and writes output to `dist/`. It also copies `images/` and `data/` into `dist/`.
- `serve.py` : **当前唯一后端**。产品 CRUD + 联系表单 + SMTP + 图片上传 + 分类管理 + 搜索 API + 管理后台 + 审计日志 + 自动构建。JSON 文件存储。
- `backend/main.py` : FastAPI 后端入口，**保留参考，暂不使用。日常开发走 serve.py。**
- `backend/routes/products.py` : Product category and CRUD API routes. Uses `pydantic.BaseModel` for request payload validation and raw SQL with `pymysql` through `backend/database.py`.
- `backend/database.py` : Simple wrapper around `pymysql` connection and cursor management.
- `backend/config.py` : Contains MySQL connection config and upload/static file settings. ⚠️ 含空白 MySQL 密码，不要部署到公网。
- `static-server.js` : **已废弃**，待删除（见 IMPROVEMENT-PLAN.md P0-4）。

## 文档索引

| 文档 | 用途 |
|------|------|
| [DEVELOPMENT.md](docs/DEVELOPMENT.md) | 开发文档 — 架构、约定、部署方案 |
| [DEVLOG.md](docs/DEVLOG.md) | 开发日志 — 历史工作记录和踩坑 |
| [IMPROVEMENT-PLAN.md](docs/IMPROVEMENT-PLAN.md) | 改进路线图 — 待做事项和优先级 |
| [Claude-Codex改进计划.md](docs/Claude-Codex改进计划.md) | AI 协作记录 — Claude + Codex 联合方案 |

## Runtime and development notes
- Python is the primary backend runtime.
- 开发服务器：`PYTHONIOENCODING=utf-8 python serve.py`（端口 8080，含全部 API）
- FastAPI 后端保留参考：`python backend/main.py`（端口 8000，暂不使用）
- Typical commands:
  - `PYTHONIOENCODING=utf-8 python build.py`
  - `PYTHONIOENCODING=utf-8 python serve.py`
- Backend depends on `fastapi`, `uvicorn`, `pymysql`（无 requirements.txt，见 P0-1）
- `backend/main.py` 硬编码了 Windows 路径（`ADMIN_HTML = r"C:\Users\11193\www\backend\admin.html"`），因为 backend/ 暂不使用，此问题标记为 IMPROVEMENT-PLAN.md P0-3（P2 优先级，等复用时修复）。

## Important conventions
- HTML templates are static files; `build.py` performs the only HTML composition step.
- All Python source files use UTF-8 encoding and simple procedural style.
- `backend/uploads` is mounted at `/uploads` and should be treated as runtime storage.
- The backend uses SQL query strings with `%s` placeholders and a `DictCursor` return shape.

## What to watch for
- There is no `requirements.txt`, `pyproject.toml`, or `venv` config（见 IMPROVEMENT-PLAN.md P0-1）
- `backend/config.py` includes a blank MySQL password and `root` user; update for secure deployments.
- `build.py` only processes root-level `.html` files and skips files without the placeholder `<!-- #include nav.html -->`.

## Recommended next customizations
- 参见 [IMPROVEMENT-PLAN.md](docs/IMPROVEMENT-PLAN.md) — 所有待办项按 P0/P1/P2/P3 分级
- 已完成工作的历史记录见 [DEVLOG.md](docs/DEVLOG.md)

