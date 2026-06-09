---
name: hex-grid-centering-lessons
description: 六边形阵列的居中、自适应和比例保持经验
metadata: 
  node_type: memory
  type: project
  originSessionId: 7e3421a6-d2a6-4ce8-8194-d84bf0311572
---

## 一、正方形容器 + 正六边形公式

### 容器自适应

用 CSS container queries 让 grid 自动取 gold-bg 短边的百分比：

```css
.banner-gold-bg { container-type: size; }
.banner-product-grid { width: min(95cqi, 95cqb); aspect-ratio: 1; position: relative; }
```

- `cqi` = container inline size（≈ 容器内容宽）
- `cqb` = container block size（≈ 容器内容高）
- `min(Xcqi, Xcqb)` = 取短边的 X%
- `aspect-ratio: 1` = 保持正方形

### 正六边形比例

对于 `clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%)`（尖头在左右）：

- **w/h = 2/√3 ≈ 1.155** 才是正六边形
- 蜂窝步长：水平 = 0.75w，垂直 = 0.5h

### 正方形容器（边长 S）中 7 个六边形位置

```
w = 完美贴合宽度%, h = 完美贴合高度%, w/h = 2/√3
最优: h = 100/3 ≈ 33.33%, w = 33.33 × 2/√3 ≈ 38.49%

#1 中心: (50%, 50%)
#2 正上: (50%, 50% - h)
#3 右上: (50% + 0.75w, 50% - 0.5h)
#4 右下: (50% + 0.75w, 50% + 0.5h)
#5 正下: (50%, 50% + h)
#6 左下: (50% - 0.75w, 50% + 0.5h)
#7 左上: (50% - 0.75w, 50% - 0.5h)
```

桌面端具体值（w=38.49%, h=33.33%）：
```css
.banner-product-item { width: 38.49%; height: 33.33%; }
.banner-product-item:nth-child(1) { left: 50%;    top: 50%;    transform: translate(-50%, -50%); z-index: 7; }
.banner-product-item:nth-child(2) { left: 50%;    top: 16.67%; transform: translate(-50%, -50%); z-index: 6; }
.banner-product-item:nth-child(3) { left: 78.87%; top: 33.33%; transform: translate(-50%, -50%); z-index: 6; }
.banner-product-item:nth-child(4) { left: 78.87%; top: 66.67%; transform: translate(-50%, -50%); z-index: 6; }
.banner-product-item:nth-child(5) { left: 50%;    top: 83.33%; transform: translate(-50%, -50%); z-index: 6; }
.banner-product-item:nth-child(6) { left: 21.13%; top: 66.67%; transform: translate(-50%, -50%); z-index: 6; }
.banner-product-item:nth-child(7) { left: 21.13%; top: 33.33%; transform: translate(-50%, -50%); z-index: 6; }
```

## 二、缝隙计算 —— 核心坑 ⚠️

**两个相邻六边形各缩一点，缝隙是两倍的单边缩量。**

因为缝隙 = 六边形A的缩量 + 六边形B的缩量 = 2×单边缩量。

如果 hover 用 `scale(1.15)` 放大填充缝隙：

```
贴合尺寸 = 完美无缝尺寸
基础尺寸 = 贴合尺寸 × (1 - (1.15-1)/2) = 贴合尺寸 × 0.925
```

即：先算单边膨胀量 (0.15/2=0.075)，基础尺寸 = 贴合尺寸 × (1-0.075) = 贴合尺寸 × 0.925。

实际值：w = 38.49 × 0.925 = 35.60%（取约 35.98%），h = 33.33 × 0.925 = 30.83%（取约 31.16%）。

**❌ 错误**：直接用 贴合尺寸 ÷ 1.15 → 缝隙过大（因为没考虑缝隙由两边的缩量叠加）

## 三、container queries 注意事项

- `container-type: size` 会施加 `contain: size`，容器尺寸必须由外部决定（如 flex 布局），不能靠内容撑开
- 在 flex row 中，gold-bg 的高度由 flex 行高决定，不受 contain 影响 → 安全
- 移动端 flex column 中用 `flex: 1` 或 `height: 100%` 明确高度 → 安全
- 同一套 item 百分比在桌面端和移动端通用（因为容器始终是正方形）

## 四、其他经验

1. **`aspect-ratio` 在 `position: absolute` 元素上不可靠**：用固定像素或 container query 代替
2. **CSS Grid `place-items: center`** 需要父容器有显式 `height`，仅 `min-height` 不够
3. **不要轻易把固定像素改成百分比**：先理解原版定位方式，再逐步迁移
4. **每次改动后都要在 F12 Computed 面板验证实际尺寸**
5. **PYTHONIOENCODING=utf-8** 解决 Windows bash 中文乱码

## 五、移动端

```css
.banner { flex-direction: column; height: 100svh; }
.banner-slide-bg { flex-direction: column; }
.banner-dark-bg { min-height: 250px; }
.banner-gold-bg { width: 100%; height: 100%; padding: 20px; }
/* grid 和 item 用同一套百分比，container query 自动适配 */
```

**How to apply:** 任何涉及六边形阵列的修改，先算正方形容器的完美贴合值（w=38.49%, h=33.33%），再根据 scale 反推基础尺寸：基础 = 贴合 × (1 - (scale-1)/2)。
