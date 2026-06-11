# 产品回收站实现方案

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为管理后台新增产品回收站功能，删除产品时移入回收站而非永久删除，支持恢复和彻底删除。

**Architecture:** 新增 data/products-trash.json 存储被删除产品（附加 deletedAt 时间戳）。修改 serve.py 的 do_DELETE 逻辑：从数组中移除产品 → 写入 trash 文件。新增 GET /api/products/trash、POST /api/products/trash/restore/{id}、DELETE /api/products/trash/{id} 三个 API。管理后台新增"回收站"Tab。

**Tech Stack:** Python 3、JSON 文件存储、原生 HTML/CSS/JS

**处理对象:** 4 个产品 + 后续新增产品

---

## 影响范围

| 文件 | 操作 | 说明 |
|------|------|------|
| serve.py | 修改 | 新增 trash 读写函数、修改 do_DELETE、新增 3 个 API 路由 |
| ackend/admin.html | 修改 | 新增回收站 Tab、trash 列表 UI、恢复/彻底删除按钮 |
| data/products-trash.json | 新建 | 存储被删除产品 |

uild.py 和 .gitignore 不涉及。

---

## 数据模型

data/products-trash.json 格式 (与 products.json 结构一致，只多一个字段):

`json
[
  {
    "id": "1061418",
    "title": "1061418EPB执行器MGU电机",
    "cat": "车用马达",
    ...所有原有字段...,
    "deletedAt": "2026-06-11 15:49:20"
  }
]
`

---

## API 设计

### GET /api/products/trash
返回回收站中所有产品列表。管理后台通过此接口获取数据。

### POST /api/products/trash/restore/{id}
将指定产品从回收站恢复到 products.json，从 trash 中移除。

### DELETE /api/products/trash/{id}
永久删除。从 trash 文件中移除该产品。

---

## 实施步骤

> 预估总工时：45 分钟。4 个 Task，每步独立可测。

---

### Task 1: 回收站数据层 (10 分钟)

**文件：**
- 修改: serve.py — 新增两个函数 + 修改 do_DELETE

- [ ] **步骤 1: 新增 load_trash() 和 save_trash() 函数**

在 serve.py 的 PRODUCTS_JSON 常量定义区域（第 20 行附近）后追加:

`python
PRODUCTS_TRASH_JSON = os.path.join(DATA_DIR, 'products-trash.json')

def load_trash():
    """从 products-trash.json 读取回收站产品"""
    if not os.path.exists(PRODUCTS_TRASH_JSON):
        return []
    with open(PRODUCTS_TRASH_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_trash(trash):
    """保存回收站数据"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PRODUCTS_TRASH_JSON, 'w', encoding='utf-8') as f:
        json.dump(trash, f, ensure_ascii=False, indent=2)
`

- [ ] **步骤 2: 修改 do_DELETE，删除时移入回收站而非丢弃**

将当前 do_DELETE（约第 379-398 行）替换为:

`python
    def do_DELETE(self):
        # /api/products/{id} — 移入回收站
        m = re.match(r'^/api/products/(.+)$', self.path)
        if m:
            pid = m.group(1)
            products = load_products()
            idx = next((i for i, p in enumerate(products) if p.get('id') == pid), None)
            if idx is None:
                self._json_response(404, {'error': '产品不存在'})
                return
            deleted_product = dict(products[idx])  # 浅拷贝
            deleted_product['deletedAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            products.pop(idx)
            save_products(products)
            # 移入回收站
            trash = load_trash()
            trash.append(deleted_product)
            save_trash(trash)
            log_audit('delete', pid, deleted_product.get('title', ''), '移入回收站')
            print(f'[OK] 产品 {pid} 已移入回收站')
            self._json_response(200, {'ok': True, 'trashId': pid})
            return

        # /api/products/trash/{id} — 永久删除
        m = re.match(r'^/api/products/trash/(.+)$', self.path)
        if m:
            pid = m.group(1)
            trash = load_trash()
            before = len(trash)
            trash = [t for t in trash if t.get('id') != pid]
            if len(trash) == before:
                self._json_response(404, {'error': '回收站中未找到该产品'})
                return
            save_trash(trash)
            print(f'[OK] 产品 {pid} 已永久删除')
            self._json_response(200, {'ok': True})
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not Found')
`

注意: 原有的 atch-delete 暂不改——批量删除较少使用且涉及面广，先不做。

- [ ] **步骤 3: 启动 serve.py 验证**

启动 python serve.py，确认无 ImportError/AttributeError。

---

### Task 2: 回收站 API 端点 (10 分钟)

**文件：**
- 修改: serve.py — 在 do_GET 和 do_POST 中新增路由

- [ ] **步骤 1: do_GET 新增回收站列表路由**

在 do_GET 的 /api/categories 之后（第 343 行后）追加:

`python
        # API: 回收站列表
        if self.path == '/api/products/trash':
            trash = load_trash()
            self._json_response(200, trash)
            return
`

- [ ] **步骤 2: do_POST 新增恢复路由**

在 do_POST 的现有路由之后、else: 之前追加:

`python
        else:
            # /api/products/trash/restore/{id}
            m = re.match(r'^/api/products/trash/restore/(.+)$', self.path)
            if m:
                pid = m.group(1)
                trash = load_trash()
                idx = next((i for i, t in enumerate(trash) if t.get('id') == pid), None)
                if idx is None:
                    self._json_response(404, {'error': '回收站中未找到该产品'})
                    return
                restored = dict(trash[idx])
                restored.pop('deletedAt', None)
                trash.pop(idx)
                save_trash(trash)
                # 恢复到产品列表
                products = load_products()
                products.append(restored)
                save_products(products)
                log_audit('restore', pid, restored.get('title', ''), '从回收站恢复')
                print(f'[OK] 产品 {pid} 已恢复')
                self._json_response(200, {'ok': True, 'product': restored})
                return
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
`

> **注意**: 此处 else: 分支需调整——原来的 else: 是最后的 404 fallback。需要把 /api/products/trash/restore/{id} 匹配放在 else: 之前，保持原来的 404 fallback 在最后。

实际代码结构应为:

`python
    def do_POST(self):
        if self.path == '/api/contact':
            self._handle_contact()
        elif self.path == '/api/products':
            self._handle_add_product()
        elif self.path == '/api/products/batch-delete':
            self._handle_batch_delete()
        elif self.path == '/api/categories/save':
            self._handle_save_categories()
        else:
            m = re.match(r'^/api/products/trash/restore/(.+)$', self.path)
            if m:
                pid = m.group(1)
                (恢复逻辑...)
                return
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
`

- [ ] **步骤 3: curl 验证三个 API**

重启 serve.py 后执行:

`ash
# 1. 回收站列表
curl -s http://localhost:8080/api/products/trash
# 预期: [] (当前回收站为空)

# 2. 删除一个产品后验证回收站
curl -X DELETE http://localhost:8080/api/products/1030837
curl -s http://localhost:8080/api/products/trash
# 预期: 包含 1030837 及 deletedAt 字段

# 3. 恢复产品
curl -X POST http://localhost:8080/api/products/trash/restore/1030837
curl -s http://localhost:8080/api/products/trash
# 预期: []
curl -s http://localhost:8080/api/products | python -c "import sys,json; print(len(json.load(sys.stdin)))"
# 预期: 3
`

---

### Task 3: 管理后台回收站 UI (20 分钟)

**文件：**
- 修改: ackend/admin.html — 新增 Tab + 列表 + 交互

- [ ] **步骤 1: 新增 Tab 按钮**

在管理后台顶部的 Tab 导航区追加回收站 Tab。参考现有结构，在上传图片 Tab 之后添加。

**位置**: 现有 Tab 列表 (产品列表、上传图片、分类编辑、操作日志) 之后，产品列表 Tab 内容区域之后。

**新增 Tab 按钮** (在现有 Tab 按钮组的末尾):

`html
<button class="admin-tab-btn" data-tab="trash">🗑️ 回收站</button>
`

**新增 Tab 内容区** (在现有 Tab 内容区域末尾):

`html
<!-- 回收站 Tab -->
<div class="admin-tab-content" id="tab-trash">
    <div class="admin-section">
        <h2>回收站</h2>
        <p style="color: #888; margin-bottom: 16px;">被删除的产品保存在此，可恢复或永久删除。</p>
        <table id="trash-table" style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="border-bottom: 1px solid #333;">
                    <th style="text-align: left; padding: 8px;">产品 ID</th>
                    <th style="text-align: left; padding: 8px;">产品名称</th>
                    <th style="text-align: left; padding: 8px;">分类</th>
                    <th style="text-align: left; padding: 8px;">删除时间</th>
                    <th style="text-align: right; padding: 8px;">操作</th>
                </tr>
            </thead>
            <tbody id="trash-tbody">
                <tr><td colspan="5" style="padding: 24px; text-align: center; color: #666;">回收站为空</td></tr>
            </tbody>
        </table>
    </div>
</div>
`

- [ ] **步骤 2: JS 逻辑 — 加载回收站列表**

在 <script> 块中新增函数:

`javascript
async function loadTrash() {
    const tbody = document.getElementById('trash-tbody');
    try {
        const resp = await fetch('/api/products/trash');
        const trash = await resp.json();
        if (!trash.length) {
            tbody.innerHTML = '<tr><td colspan="5" style="padding: 24px; text-align: center; color: #666;">回收站为空</td></tr>';
            return;
        }
        tbody.innerHTML = trash.map(p => 
            <tr style="border-bottom: 1px solid #222;">
                <td style="padding: 8px;"></td>
                <td style="padding: 8px;"></td>
                <td style="padding: 8px;"></td>
                <td style="padding: 8px; color: #888;"></td>
                <td style="padding: 8px; text-align: right;">
                    <button onclick="restoreProduct('')" style="background: #4CAF50; border: none; color: #fff; padding: 4px 12px; border-radius: 4px; cursor: pointer; margin-right: 6px;">恢复</button>
                    <button onclick="permanentDelete('')" style="background: #f44336; border: none; color: #fff; padding: 4px 12px; border-radius: 4px; cursor: pointer;">彻底删除</button>
                </td>
            </tr>
        ).join('');
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="5" style="padding: 24px; text-align: center; color: #f44336;">加载失败</td></tr>';
    }
}
`

- [ ] **步骤 3: JS 逻辑 — 恢复和彻底删除**

`javascript
async function restoreProduct(id) {
    if (!confirm(确定恢复产品 ？)) return;
    try {
        const resp = await fetch(/api/products/trash/restore/, { method: 'POST' });
        const data = await resp.json();
        if (data.ok) {
            alert('已恢复');
            loadTrash();
            loadProducts(); // 刷新产品列表 (调用已有函数)
        } else {
            alert('恢复失败: ' + (data.error || '未知错误'));
        }
    } catch (e) {
        alert('恢复失败');
    }
}

async function permanentDelete(id) {
    if (!confirm(确定永久删除产品 ？此操作不可恢复！)) return;
    try {
        const resp = await fetch(/api/products/trash/, { method: 'DELETE' });
        const data = await resp.json();
        if (data.ok) {
            alert('已永久删除');
            loadTrash();
        } else {
            alert('删除失败: ' + (data.error || '未知错误'));
        }
    } catch (e) {
        alert('删除失败');
    }
}
`

- [ ] **步骤 4: Tab 切换触发加载**

在现有的 Tab 切换逻辑中，当切换到 	rash Tab 时调用 loadTrash()。找到 Tab 切换的 click 事件处理，在 switch 或 if-else 分支中添加:

`javascript
if (tabId === 'trash') {
    loadTrash();
}
`

完整的 Tab 切换逻辑需要查看现有 admin.html 代码。核心原则: 切换到回收站 Tab 时触发 loadTrash()，从回收站恢复产品后同时刷新产品列表。

- [ ] **步骤 5: 视觉验证**

浏览器打开 http://localhost:8080/admin，切换回收站 Tab:
- 默认显示"回收站为空"
- 删除产品后切换到回收站 Tab，显示已删除产品列表
- 点击"恢复"，产品回到产品列表，回收站清空
- 点击"彻底删除"，产品从回收站消失

---

### Task 4: 修复当前测试产品恢复 (5 分钟)

**目的**: 本次验收时删除的 1061418 已无法通过 trash 恢复 (因为新机制在删除之后才生效)。手动重建该产品。

- [ ] **步骤 1: 手动写入产品数据到 products.json**

根据审计日志 udit.json 中的记录 (1061418 EPB执行器MGU电机, 3 张主图, 2 张详情图)，产品数据无法完全还原 (缺少原始图片路径)。最低恢复:

`ash
# 如果用户需要恢复这个产品，在管理后台手动新增即可
# 因为管理员录入的原始字段 (desc, specs, images) 只有当时知道
`

> **注意**: 这个产品是验收时的测试数据，是否需要恢复取决于用户。如果需要，最简单的方式是在管理后台重新录入。

---

## 不做

| 项 | 理由 |
|----|------|
| 批量删除进回收站 | atch-delete 使用频率极低，先保持直接删除 |
| 回收站自动清理 (30 天过期) | 过度设计，手动永久删除足够 |
| 回收站搜索/筛选 | 产品总量 < 100，表格直接浏览即可 |
| .gitignore 追加 products-trash.json | 回收站数据应纳入 git 跟踪，和 products.json 同等对待 |

---

> 制定日期: 2026-06-11
