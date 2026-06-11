# 产品图片管理改进方案

> 2026-06-11，针对新增产品时的两个图片问题。

---

## 问题一：图片无法拖拽排序

### 现状

`backend/admin.html` 已有拖拽排序的部分实现（第 310-354 行），但存在 **3 个 bug** 导致功能不可用：

| Bug | 位置 | 现象 |
|-----|------|------|
| **#1 跨网格污染** | `addFilesToGrid()` 第 364 行 | `renderImgGrid('mainImgGrid', mainImgItems)` 硬编码了 `mainImgGrid`，导致上传详情图时主网格被错误刷新 |
| **#2 无跨网格防护** | `renderImgGrid()` 第 321 行 | `ondrop` 没有校验拖放是否发生在同一网格内。从主图网格拖到详情网格会同时破坏两个数组 |
| **#3 触摸端不支持** | 全局 | 无 `touchstart`/`touchmove`/`touchend` 事件，移动端（iPad/手机）无法拖拽排序 |

### 方案

修复 `renderImgGrid()` 和 `addFilesToGrid()`，追加移动端触摸事件。

#### 改动 1：修复 `addFilesToGrid()` — 去硬编码

```diff
 function addFilesToGrid(items, files, maxCount) {
   var remaining = maxCount - items.length;
   var toAdd = Math.min(files.length, remaining);
   for (var i=0; i<toAdd; i++) {
     var reader = new FileReader();
+    var targetGridId = (items === mainImgItems) ? 'mainImgGrid' : 'detailImgGrid';
     (function(file){
       reader.onload = function(e){
         items.push({src: e.target.result, keepPath: null, file: file});
-        renderImgGrid('mainImgGrid', mainImgItems);
-        renderImgGrid('detailImgGrid', detailImgItems);
+        renderImgGrid(targetGridId, items);
       };
       reader.readAsDataURL(file);
     })(files[i]);
   }
 }
```

#### 改动 2：`drop` 事件加同网格校验

```diff
 div.ondrop = function(e){
   e.preventDefault();
   this.classList.remove('drag-over');
+  // 禁止跨网格拖放
+  if (!dragSrc || dragSrc.parentElement !== this.parentElement) return;
   var fromIdx = parseInt(dragSrc.getAttribute('data-idx'));
   var toIdx = parseInt(this.getAttribute('data-idx'));
   if (fromIdx !== toIdx) {
     var tmp = items[fromIdx];
     items.splice(fromIdx, 1);
     items.splice(toIdx, 0, tmp);
     renderImgGrid(gridId, items);
   }
 };
```

#### 改动 3：追加移动端触摸拖拽

在 `renderImgGrid()` 的 item 创建逻辑中，追加 touch 事件：

```javascript
// 移动端触摸拖拽
var touchStartX = 0, touchStartY = 0, touchItem = null;

div.addEventListener('touchstart', function(e){
  touchItem = this;
  touchStartX = e.touches[0].clientX;
  touchStartY = e.touches[0].clientY;
  this.style.opacity = '0.6';
}, {passive: true});

div.addEventListener('touchmove', function(e){
  e.preventDefault();
}, {passive: false});

div.addEventListener('touchend', function(e){
  this.style.opacity = '1';
  if (!touchItem) return;
  var endX = e.changedTouches[0].clientX;
  var endY = e.changedTouches[0].clientY;
  var dx = endX - touchStartX;
  var dy = endY - touchStartY;
  // 移动超过 30px 才触发
  if (Math.abs(dx) < 30 && Math.abs(dy) < 30) { touchItem = null; return; }
  
  // 找到手指松开位置下方的元素
  var targetEl = document.elementFromPoint(endX, endY);
  var targetItem = targetEl ? targetEl.closest('.img-grid-item') : null;
  if (!targetItem || targetItem === touchItem || targetItem.parentElement !== touchItem.parentElement) {
    touchItem = null; return;
  }
  
  var fromIdx = parseInt(touchItem.getAttribute('data-idx'));
  var toIdx = parseInt(targetItem.getAttribute('data-idx'));
  var tmp = items[fromIdx];
  items.splice(fromIdx, 1);
  items.splice(toIdx, 0, tmp);
  renderImgGrid(gridId, items);
  touchItem = null;
});
```

### 验收标准

- [ ] 主图网格内拖拽重排正常（桌面端鼠标 + 移动端触摸）
- [ ] 详情图网格内拖拽重排正常
- [ ] 从主图网格拖到详情图网格 → 不触发交换
- [ ] 保存产品后，图片顺序与拖拽后的顺序一致
- [ ] 删除中间图片后，剩余图片保持原有顺序

---

## 问题二：卡片图未统一裁剪

### 现状

产品卡片图来自 `cardImage` 字段（若为空则取 `images[0]`）。不同产品上传的图片比例各异，导致：

- `product-card-img` 使用 `object-fit: contain` → 不同比例图片留白不一致
- 卡片视觉不整齐，专业感打折扣

### 方案

**纯 CSS 方案**（推荐，零依赖，10 分钟）：

1. 卡片图容器固定宽高比
2. 将 `object-fit: contain` 改为 `object-fit: cover`
3. 确认 `product-card` 在所有页面效果一致

#### 改动位置

**`css/products.css`** — 产品卡片图容器：

```diff
 .product-card-img {
-    /* 当前如果有 object-fit: contain，替换为 cover */
+    width: 100%;
+    aspect-ratio: 4 / 3;       /* 统一 4:3 比例 */
+    overflow: hidden;
+    background: #1a1a2e;        /* 图片加载前的底色 */
 }
 .product-card-img img {
     width: 100%;
     height: 100%;
-    object-fit: contain;
+    object-fit: cover;          /* 裁剪填充，不留白 */
 }
```

**`build.py`** — `generate_card()` 函数中的 img 行（第 78 行），确认 inline style 也改为 cover：

```diff
- img_html = f'<img src="{img_src}" alt="{title}" style="width:100%;height:100%;object-fit:contain;">'
+ img_html = f'<img src="{img_src}" alt="{title}" style="width:100%;height:100%;object-fit:cover;">'
```

### 备选：Canvas 裁剪方案（如需物理裁剪文件）

如果纯 CSS 不够（比如图片文件太大需要物理缩略图），可以在上传卡片图时用 Canvas 生成固定尺寸的缩略图。但考虑到产品 <100 个，CSS `object-fit: cover` + 浏览器缓存足够。

### 验收标准

- [ ] 所有产品卡片图比例统一（4:3）
- [ ] 上传不同比例图片（横图、竖图、方图）后，卡片展示一致
- [ ] 产品中心页、首页六边形、子类目页的卡片图全部统一
- [ ] 详情页主图不受影响（主图仍 `object-fit: contain`）

---

## 实施工时

| 项目 | 改动文件 | 预估 |
|------|---------|------|
| Bug #1 | `admin.html` `addFilesToGrid()` | 5 分钟 |
| Bug #2 | `admin.html` `renderImgGrid()` drop 事件 | 2 分钟 |
| Bug #3 | `admin.html` `renderImgGrid()` + touch 事件 | 20 分钟 |
| 卡片图裁剪 | `css/products.css` + `build.py` | 10 分钟 |
| **合计** | 3 个文件 | **~40 分钟** |

---

## 评估审核意见（2026-06-11）

> 代码核实通过，方案整体可行。以下为 3 个改进建议，以原文 vs 建议的对比形式呈现。

### 评估 1：Bug #1 传参方式优化

**原文**：
``javascript
function addFilesToGrid(items, files, maxCount) {
  var remaining = maxCount - items.length;
  var toAdd = Math.min(files.length, remaining);
  for (var i=0; i<toAdd; i++) {
    var reader = new FileReader();
+   var targetGridId = (items === mainImgItems) ? 'mainImgGrid' : 'detailImgGrid';
    (function(file){
      reader.onload = function(e){
        items.push({src: e.target.result, keepPath: null, file: file});
-       renderImgGrid('mainImgGrid', mainImgItems);
-       renderImgGrid('detailImgGrid', detailImgItems);
+       renderImgGrid(targetGridId, items);
      };
      reader.readAsDataURL(file);
    })(files[i]);
  }
}
``

**建议**：不在函数内部判断引用相等，由调用侧直接传入 gridId，更直观：

``javascript
function addFilesToGrid(items, files, maxCount, gridId) {
  var remaining = maxCount - items.length;
  var toAdd = Math.min(files.length, remaining);
  for (var i=0; i<toAdd; i++) {
    var reader = new FileReader();
    (function(file){
      reader.onload = function(e){
        items.push({src: e.target.result, keepPath: null, file: file});
+       renderImgGrid(gridId, items);
      };
      reader.readAsDataURL(file);
    })(files[i]);
  }
}

function handleMainImgSelect() {
  var files = document.getElementById('mainImgInput').files;
- addFilesToGrid(mainImgItems, files, 6);
+ addFilesToGrid(mainImgItems, files, 6, 'mainImgGrid');
  ...
}
function handleDetailImgSelect() {
  var files = document.getElementById('detailImgInput').files;
- addFilesToGrid(detailImgItems, files, 10);
+ addFilesToGrid(detailImgItems, files, 10, 'detailImgGrid');
  ...
}
``

**理由**：(items === mainImgItems) 引用判等在复杂编辑场景可能失败——两个数组来自不同来源时不是同一个引用。

---

### 评估 2：Bug #3 touchmove 拦截范围过宽

**原文**：
``javascript
div.addEventListener('touchmove', function(e){
  e.preventDefault();
}, {passive: false});
``

e.preventDefault() 无条件拦截所有 	ouchmove，如果用户只是滚动页面而手指触碰到了图片区域，页面无法滚动。

**建议**：只有正在拖拽时（	ouchItem === this）才拦截：

``javascript
div.addEventListener('touchmove', function(e){
  if (touchItem === this) e.preventDefault();
}, {passive: false});
``

---

### 评估 3：卡片图移动端高度冲突

css/products.css 第 310 行存在移动端覆写：

``css
/* 移动端 */
.product-card-img {
    height: 130px;
    flex: none;
}
``

原文改动在桌面端 .product-card-img 添加了 spect-ratio: 4 / 3，但移动端 height: 130px 固定值会和比例约束冲突。

**原文**（仅改桌面端）：
``diff
 .product-card-img {
+    width: 100%;
+    aspect-ratio: 4 / 3;
+    overflow: hidden;
+    background: #1a1a2e;
 }
``

**建议**（同步修改移动端）：
``diff
 /* 桌面端 */
 .product-card-img {
+    width: 100%;
+    aspect-ratio: 4 / 3;
+    overflow: hidden;
+    background: #1a1a2e;
 }

 /* 移动端 — 去掉固定高度，沿用 aspect-ratio */
 .product-card-img {
-    height: 130px;
-    flex: none;
+    flex: none;
 }
``

---

### 汇总

| 评估项 | 原文问题 | 建议 |
|--------|---------|------|
| Bug #1 传参 | ddFilesToGrid 内部引用判等 | 由调用侧传入 gridId 参数 |
| Bug #3 touchmove | 无条件 preventDefault 阻止滚动 | 仅在拖拽时拦截 |
| 卡片图移动端 | height: 130px 与 spect-ratio 冲突 | 删除固定高度，保留 lex: none |

三个改进均为防御性修正，不影响原方案的核心逻辑。

---

### 评估 4：删除按钮的 idx 闭包安全性

**疑点**：del.onclick 闭包捕获了 orEach 循环中的 idx。从数组中间删除一个元素后，后续元素的索引前移，如果还有其他按钮的闭包残留，它们持有的 idx 就会指向错误的元素。

**验证结果**：当前代码**无此问题**。原因：

- del.onclick 删除逻辑为 items.splice(idx, 1); renderImgGrid(gridId, items);
- enderImgGrid 开头执行 grid.innerHTML = ''，**全量清理**所有旧 DOM 节点和它们的事件处理器
- 删除操作立即触发全量重渲染，所有按钮获得新的、正确的 idx 闭包
- JS 单线程执行，不存在"第一个删除还没渲染完就点第二个"的竞态

**技术债标记**：上述安全性依赖于"每次操作都全量重渲染"这个设计。如果将来优化为局部 DOM 更新（emoveChild 单个节点 + 手动更新后续 data-idx），必须同步处理。建议在 enderImgGrid 函数上方加注释：

``javascript
// WARNING: This function does full DOM rebuild (innerHTML = '').
// All event handlers are refreshed every call. If changing to partial
// update, ensure del.onclick closures are re-bound with correct idx.
function renderImgGrid(gridId, items) {
``

**结论**：当前无 Bug，但属于脆弱设计，加注释即可。

---

## 📋 复审意见（2026-06-11）

> 对评估审核意见的逐条复核 + 补充发现。

---

### 评估 1 复核：传参方式 ✅ 建议采纳

评估 1 的建议（`gridId` 作为参数传入）是合理的防御性改进。但需注意一点：

当前代码中 `mainImgItems` 和 `detailImgItems` 是模块级 `var`，引用永不变，`items === mainImgItems` 在现有调用路径下**永远正确**。这不是 bug，只是脆弱设计。

采纳建议时需确认调用侧**确实改了**：

```diff
- addFilesToGrid(mainImgItems, files, 6);
+ addFilesToGrid(mainImgItems, files, 6, 'mainImgGrid');
- addFilesToGrid(detailImgItems, files, 10);
+ addFilesToGrid(detailImgItems, files, 10, 'detailImgGrid');
```

➡️ **采纳，实施时确认两处调用侧同步修改。**

---

### 评估 2 复核：touchmove 拦截 ✅ 确实会卡滚动

确认。当前代码在图片网格区域内手指触摸滑动时，页面无法滚动。评估 2 的修正方案 `if (touchItem === this) e.preventDefault()` 正确。

➡️ **采纳。**

---

### 评估 3 复核：移动端高度冲突 ✅ 确认存在

验证了 `css/products.css` 移动端覆写确实存在。`height: 130px` + `aspect-ratio: 4/3` 会互相冲突——浏览器会选一个赢，结果不可预测。

修正方案删除 `height: 130px` 是正确的，但需额外确认一点：去掉固定高度后，卡片在小屏上是否仍然好看。建议实施后在 Chrome DevTools 375px 宽度下目视验证。

➡️ **采纳，实施后移动端目视验证。**

---

### 评估 4 复核：idx 闭包安全性 ✅ 分析正确

确认：`renderImgGrid` 的 `innerHTML = ''` 全量重渲染使得每次删除后的 idx 都是新的，不会出现越界或错位。加注释的建议合理。

➡️ **采纳，实施时加注释。**

---

### 🆕 补充发现 1：`touchend` 的 `elementFromPoint` 边界情况

```javascript
var targetEl = document.elementFromPoint(endX, endY);
var targetItem = targetEl ? targetEl.closest('.img-grid-item') : null;
```

如果用户把图片拖到网格区域之外再松手，`elementFromPoint` 返回 `null` 或网格外的元素，`targetItem` 为 `null`，排序不会触发——这是正确的静默降级。

但有一个边界：如果网格中只有 1 张图，拖拽后松手位置恰好在同一张图上（`targetItem === touchItem`），排序不会触发。这也正确——只有 1 张图没什么可排的。

➡️ **无 Bug，设计合理。**

---

### 🆕 补充发现 2：`addFilesToGrid` 中的并发竞态

`addFilesToGrid` 使用 `FileReader.onload`（异步回调）。如果用户在上传过程中点击了某张图的删除按钮：

```
1. addFilesToGrid 启动 reader1, reader2
2. reader1.onload 触发 → item push → renderImgGrid (重建DOM)
3. 用户点删除 → items.splice → renderImgGrid (重建DOM)  
4. reader2.onload 触发 → item push → renderImgGrid (重建DOM)
   ↑ 步骤3删除的图可能又被 reader2 加了回来
```

**实际影响**：极低。`reader.onload` 执行速度（<50ms）远快于人类点击速度，且 `FileReader` 是异步但微任务队列在同一次事件循环中处理。除非刻意在上传瞬间快速点击删除，否则不会碰到。

➡️ **不修，标注为已知限制。**

---

### 复审总结

| 评估项 | 原判断 | 复审 |
|--------|--------|------|
| 评估 1 传参 | 建议改进 | ✅ 采纳，确认调用侧同步改 |
| 评估 2 touchmove | 会卡滚动 | ✅ 采纳 |
| 评估 3 高度冲突 | 移动端冲突 | ✅ 采纳，目视验证 |
| 评估 4 idx 闭包 | 无 Bug | ✅ 采纳，加注释 |
| 🆕 补充1 elementFromPoint | — | ✅ 设计合理，无 Bug |
| 🆕 补充2 reader 竞态 | — | ⚠️ 不修，标注已知限制 |

**方案整体评级**：✅ 可以执行。4 个评估 + 2 个补充发现，无阻塞问题。

> 复审日期：2026-06-11

---

## 📋 追查根因（2026-06-11）

> 实施后发现拖拽排序表现不一致：同一网格内，部分图片可拖、部分不可拖。

### 现象

| 产品 | 图片数 | 拖拽表现 |
|------|--------|----------|
| 1030837 | 3 | 仅第1张可拖 |
| 1030896 | 3 | 仅第1张可拖 |
| 1031001 | 3 | 仅第2、3张可拖，第1张不可 |
| 1061418 | 12 | 全部不可拖 |

### 根因：`<img>` 原生拖拽拦截了 `<div>` 的 HTML5 拖拽

浏览器对 `<img>` 元素有**原生拖拽行为**（拖到桌面保存图片、拖到新标签页打开等）。当 `<div draggable="true">` 内部包含 `<img>` 时，浏览器优先触发图片的原生拖拽，吃掉 `dragstart` 事件——`div` 的 `ondragstart` 根本不会触发。

是否触发原生拖拽取决于浏览器是否判定图片为"有效可拖图片"（`img.complete === true` 且 `naturalWidth > 0`），这受文件大小、缓存状态、加载时序影响，因此表现不一致。

### 定位代码

`renderImgGrid()` 函数中，创建 `<img>` 元素后未设置 `draggable = false`：

```javascript
// backend/admin.html renderImgGrid() 内
var img = document.createElement('img');
img.src = item.src;
// ← 缺少：img.draggable = false;
div.appendChild(img);
```

### 修复方案

在 `renderImgGrid()` 中，`img.src = item.src` 之后、`div.appendChild(img)` 之前，加一行：

```diff
 var img = document.createElement('img');
 img.src = item.src;
+img.draggable = false;  // 禁止原生图片拖拽，让 div 的 HTML5 拖拽接管
 div.appendChild(img);
```

`img.draggable = false` 阻止浏览器对 `<img>` 的原生拖拽拦截，确保每次拖拽都由 `<div>` 的 `ondragstart` 触发——所有图片在所有产品中行为一致。

### 附加：CSS 防御

在 admin.html 的 `<style>` 中追加一行，防止未来新增的图片元素重现此问题：

```css
.img-grid-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    user-drag: none;              /* 禁止原生图片拖拽（CSS 层防御） */
    -webkit-user-drag: none;
}
```

注意：linter 已自动添加了 `.img-grid-item img{width:100%;height:100%;object-fit:cover}`，只需在此基础上追加 `user-drag: none` 两行。

### 验证

修复后在浏览器中测试：
- 1030837：3张主图全部可拖拽排序 ✅
- 1030896：3张主图全部可拖拽排序 ✅
- 1031001：3张主图全部可拖拽排序 ✅
- 1061418：12张主图全部可拖拽排序 ✅

> 追查日期：2026-06-11
