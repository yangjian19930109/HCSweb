# 防泄漏实施方案

> 2026-06-11 代码审计结论。待用户确认后执行。

---

## 一、泄露点全部清单

| # | 载体 | 路径 | 访问方式 | 风险 |
|---|------|------|----------|------|
| 1 | `products.json` | `dist/data/products.json` | `GET /data/products.json` | 🔴 浏览器直接下载 |
| 2 | `products.js` | `data/products.js`（git 跟踪） | `git clone` 或 GitHub 浏览 | 🔴 仓库历史永久泄露 |
| 3 | `/api/products` | HTTP 端点 | `GET /api/products` | 🟡 脚本可批量抓取（后续 P2-3 处理） |

---

## 二、涉及文件

```
serve.py            ← 删除 regenerate_js() + 清理调用链
.gitignore          ← 追加 data/products.js
data/products.js    ← git rm --cached
```

`build.py` 不涉及（已验证：不引用 `products.js`，不复制 `data/` 到 `dist/`）。

---

## 三、serve.py 修改明细

### 3.1 删除 `PRODUCTS_JS` 常量（第 21 行）

```diff
- PRODUCTS_JS = os.path.join(DATA_DIR, 'products.js')
```

### 3.2 移除 `save_products()` 中的 `regenerate_js()` 调用（第 127 行）

```diff
  def save_products(products):
-     """保存产品到 products.json，重新生成 JS，自动构建"""
+     """保存产品到 products.json，自动构建"""
      os.makedirs(DATA_DIR, exist_ok=True)
      with open(PRODUCTS_JSON, 'w', encoding='utf-8') as f:
          json.dump(products, f, ensure_ascii=False, indent=2)
-     regenerate_js(products)
      # 自动重建静态页面
      auto_build()
```

### 3.3 删除 `regenerate_js()` 整个函数（第 132-206 行）

```diff
- def regenerate_js(products):
-     """根据产品数据重新生成 products.js（保留尾部搜索函数）"""
-     ...（75 行，全部删除）
```

此函数做了三件事，全部不再需要：

| 原功能 | 为什么可以删 |
|--------|-------------|
| 生成 `data/products.js` | 无页面引用，搜索已改为 `/api/search` API |
| 写入 `dist/data/products.json` | **这正是泄露源 #1** |
| 解析旧 products.js 的尾部搜索函数 | 旧 Fuse.js 逻辑，已废弃 |

### 3.4 删除启动时的 `products.js` 生成逻辑（第 802-807 行）

```diff
  if __name__ == '__main__':
      _refresh_categories()
-     # 如果 products.js 不存在，从 JSON 生成
-     if not os.path.exists(PRODUCTS_JS):
-         products = load_products()
-         if products:
-             regenerate_js(products)
-             print(f'[OK] Generated products.js from products.json ({len(products)} products)')

      os.chdir(DIR)
```

---

## 四、Git 操作

```bash
# 1. 从 git 跟踪中移除（保留本地文件以免影响运行中的 serve.py）
git rm --cached data/products.js

# 2. 追加到 .gitignore
echo "data/products.js" >> .gitignore

# 3. 删除本地文件（可选，serve.py 不再生成它之后就可以删）
rm data/products.js
```

---

## 五、构建产物清理

`serve.py` 改完后，`dist/data/products.json` 不会再有新数据写入——但旧文件依然在磁盘上，浏览器照常能访问。

`build.py` 在每次构建开头会 `shutil.rmtree(dist/data/)`，但这是被动清理——如果改完 serve.py 后没有立即构建，旧文件残留期间就是泄露窗口。

**因此必须主动删除，不能依赖 build.py 的间接清理**：

```bash
# 主动删除 — 改完 serve.py 后立刻执行
rm -rf dist/data/
```

`dist/data/` 整个目录删掉即可。`build.py` 不依赖 `dist/data/`（它从源码 `data/` 读取），下次构建时如果业务需要会自动重建空目录。

---

## 六、执行步骤 & 验证清单

### 执行步骤

1. 修改 `serve.py`（删除 3.1~3.4 所列代码）
2. `rm -rf dist/data/` ← **立刻执行**，不等 build.py
3. `git rm --cached data/products.js && echo "data/products.js" >> .gitignore`
4. `rm data/products.js`（可选，因为 serve.py 不再生成它）
5. `python build.py`（重新构建，确保一切正常）
6. 启动 `python serve.py`，逐项验证

### 验证清单

- [ ] `python serve.py` 正常启动，无 ImportError、无 AttributeError
- [ ] `curl http://localhost:8080/data/products.json` → 404
- [ ] `curl http://localhost:8080/data/products.js` → 404
- [ ] 管理后台 `/admin` → 产品列表正常加载（从 `/api/products` 读，非静态文件）
- [ ] `POST /api/products` 新增产品 → 保存成功 → `products.json` 在源码 data/ 目录正常更新
- [ ] 产品中心页 `/products.html` → 产品卡片正常显示（build.py 内联生成，不依赖 API）
- [ ] 搜索功能 `/api/search?q=xxx` → 正常返回结果
- [ ] `git status` → `data/products.js` 不再出现在跟踪列表
- [ ] 浏览器无痕窗口访问 `http://localhost:8080/data/products.json` → 404

---

## 七、变更影响范围

| 影响 | 说明 |
|------|------|
| 搜索功能 | ✅ 无影响。搜索已切到 `/api/search` API |
| 产品卡片展示 | ✅ 无影响。卡片由 `build.py` 构建时内联生成 |
| 管理后台 | ✅ 无影响。后台通过 `/api/products` API 读写 |
| 前端 scripts | ✅ 无影响。无页面引用 `products.js` |
| 旧书签/缓存 | ⚠️ 如有外部系统直接 fetch `/data/products.json`，将 404 |

---

## 八、与 P2-3（管理后台加认证）的关系

| 项 | 本轮（堵漏） | P2-3（第二波） |
|----|------------|---------------|
| 静态文件泄露 | ✅ 彻底堵死 | — |
| `/api/products` GET 认证 | ❌ 不改（后台需要） | ✅ HTTP Basic Auth |
| `/api/products` 写操作认证 | ❌ 不改 | ✅ HTTP Basic Auth |

**不放在同一轮的原因**：加 Basic Auth 需要同步修改 `backend/admin.html` 的 fetch 调用（所有请求带 `Authorization` 头），涉及前后端联调。本轮只做纯后端删除，零风险。
