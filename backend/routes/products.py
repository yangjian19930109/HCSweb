# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os, uuid
from backend.database import get_db
from backend.config import UPLOAD_DIR, MAX_FILE_SIZE, ALLOWED_EXTENSIONS

router = APIRouter()

class ProductCreate(BaseModel):
    category_id: int = None
    model: str = None
    name: str = None
    description: str = None
    specs: str = None
    featured: bool = False
    sort_order: int = 0

class ProductUpdate(BaseModel):
    category_id: int = None
    model: str = None
    name: str = None
    description: str = None
    specs: str = None
    featured: bool = None
    sort_order: int = None

@router.get("/api/categories")
def list_categories():
    db = get_db()
    try:
        db.execute("SELECT * FROM categories ORDER BY sort_order")
        return db.fetchall()
    finally:
        db.close()

@router.get("/api/products")
def list_products(category_id: int = None, keyword: str = None, featured: bool = None):
    sql = "SELECT p.*, c.name as category_name FROM products p LEFT JOIN categories c ON p.category_id = c.id WHERE 1=1"
    params = []
    if category_id is not None:
        sql += " AND p.category_id = %s"
        params.append(category_id)
    if keyword:
        sql += " AND (p.model LIKE %s OR p.name LIKE %s OR p.description LIKE %s)"
        k = "%" + keyword + "%"
        params.extend([k, k, k])
    if featured is not None:
        sql += " AND p.featured = %s"
        params.append(featured)
    sql += " ORDER BY p.sort_order, p.id"
    db = get_db()
    try:
        db.execute(sql, params)
        return db.fetchall()
    finally:
        db.close()

@router.get("/api/products/{product_id}")
def get_product(product_id: int):
    db = get_db()
    try:
        db.execute("SELECT p.*, c.name as category_name FROM products p LEFT JOIN categories c ON p.category_id = c.id WHERE p.id = %s", (product_id,))
        result = db.fetchone()
        if not result: raise HTTPException(status_code=404, detail="Not found")
        return result
    finally:
        db.close()

@router.post("/api/products")
def create_product(body: ProductCreate):
    db = get_db()
    try:
        db.execute("INSERT INTO products (category_id, model, name, description, specs, image_url, file_url, featured, sort_order) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (body.category_id, body.model, body.name, body.description, body.specs, None, None, body.featured, body.sort_order))
        db.commit()
        new_id = db.lastrowid
        return {"id": new_id, "message": "Created"}
    finally:
        db.close()

@router.put("/api/products/{product_id}")
def update_product(product_id: int, body: ProductUpdate):
    updates = []
    params = []
    if body.category_id is not None: updates.append("category_id=%s"); params.append(body.category_id)
    if body.model is not None: updates.append("model=%s"); params.append(body.model)
    if body.name is not None: updates.append("name=%s"); params.append(body.name)
    if body.description is not None: updates.append("description=%s"); params.append(body.description)
    if body.specs is not None: updates.append("specs=%s"); params.append(body.specs)
    if body.featured is not None: updates.append("featured=%s"); params.append(body.featured)
    if body.sort_order is not None: updates.append("sort_order=%s"); params.append(body.sort_order)
    if not updates: raise HTTPException(status_code=400, detail="No fields to update")
    params.append(product_id)
    db = get_db()
    try:
        db.execute("UPDATE products SET " + ",".join(updates) + " WHERE id=%s", params)
        db.commit()
        return {"message": "Updated"}
    finally:
        db.close()

@router.delete("/api/products/{product_id}")
def delete_product(product_id: int):
    db = get_db()
    try:
        db.execute("SELECT image_url,file_url FROM products WHERE id=%s", (product_id,))
        row = db.fetchone()
        if not row: raise HTTPException(status_code=404, detail="Not found")
        for url in [row["image_url"], row["file_url"]]:
            if url:
                fp = os.path.join(os.path.dirname(__file__), "..", url.lstrip("/"))
                if os.path.exists(fp): os.remove(fp)
        db.execute("DELETE FROM products WHERE id=%s", (product_id,))
        db.commit()
        return {"message": "Deleted"}
    finally:
        db.close()

