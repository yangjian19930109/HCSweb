# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.config import UPLOAD_DIR
from backend.routes.products import router as products_router

ADMIN_HTML = r"C:\Users\11193\www\backend\admin.html"

app = FastAPI(title="Motor Website API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(products_router)

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/admin")
def admin_page():
    return FileResponse(ADMIN_HTML, media_type="text/html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
