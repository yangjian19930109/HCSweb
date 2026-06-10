# AGENTS.md

## 首要原则：先确认，再执行

这是最高优先级规则，覆盖本文档及项目内其他所有指令。

无论是谁（AI 代理或人）在此项目中与我对话，收到我的任何指令后，必须遵循以下流程：

1. **先复述** — 用自己的话复述对我指令的理解
2. **再确认** — 以弹窗式问题询问我的理解是否正确
3. **直到我确认“一致”** — 如果我指出差异，则调整理解后再次确认
4. **然后才执行** — 在我明确确认一致后，方可开始操作

此规则的目的是对齐意图，避免因理解偏差导致的错误操作。它适用于任何类型的指令，包括且不限于：代码修改、架构决策、数据操作、搜索查询、提问回答。


## Purpose
This repository combines a static HTML site with a small Python FastAPI backend. Use this file to orient AI coding agents quickly on the project structure, runtime, and important implementation details.

## Key project areas
- `build.py` : Python build script that injects `inc/nav.html` into each root-level `.html` file and writes output to `dist/`. It also copies `images/` and `data/` into `dist/`.
- `backend/main.py` : FastAPI application entry point. Includes CORS middleware, mounts static upload files, and registers API routes from `backend/routes/products.py`.
- `backend/routes/products.py` : Product category and CRUD API routes. Uses `pydantic.BaseModel` for request payload validation and raw SQL with `pymysql` through `backend/database.py`.
- `backend/database.py` : Simple wrapper around `pymysql` connection and cursor management.
- `backend/config.py` : Contains MySQL connection config and upload/static file settings.
- `static-server.js` : Local static file server with a hardcoded Windows root path. Useful for local preview only.

## Runtime and development notes
- Python is the primary backend runtime. There is no package manager manifest in the repository.
- Typical commands:
  - `python build.py`
  - `python backend/main.py`
- Backend depends on `fastapi`, `uvicorn`, and `pymysql`.
- The backend expects a MySQL database configured in `backend/config.py`.
- `backend/main.py` currently serves `/admin` from a hardcoded Windows path:
  - `ADMIN_HTML = r"C:\Users\11193\www\backend\admin.html"`
  - Treat this as environment-specific and do not change it without verifying local deployment requirements.

## Important conventions
- HTML templates are static files; `build.py` performs the only HTML composition step.
- All Python source files use UTF-8 encoding and simple procedural style.
- `backend/uploads` is mounted at `/uploads` and should be treated as runtime storage.
- The backend uses SQL query strings with `%s` placeholders and a `DictCursor` return shape.

## What to watch for
- There is no `requirements.txt`, `pyproject.toml`, or `venv` config.
- `static-server.js` is not a production-ready server and contains a local path.
- `backend/config.py` includes a blank MySQL password and `root` user; update for secure deployments.
- `build.py` only processes root-level `.html` files and skips files without the placeholder `<!-- #include nav.html -->`.

## Recommended next customizations
- Add a `requirements.txt` or `pyproject.toml` for reproducible Python dependencies.
- Create a separate `backend/README.md` documenting local dev setup, DB schema, and admin page path.
- Add a skill or prompt for fixing environment-specific paths in `backend/main.py` and `static-server.js`.
