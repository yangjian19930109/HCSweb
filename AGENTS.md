# AGENTS.md

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
