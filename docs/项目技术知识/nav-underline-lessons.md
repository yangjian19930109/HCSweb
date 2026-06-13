## 最终方案

`updateNavOnScroll` 纯粹基于 section 匹配，无 fallback、无"先清空"：

```js
sections.forEach(function (section) {
    if (scrollTop >= sectionTop && scrollTop < sectionTop + sectionHeight) {
        navLinks.forEach(function (link) {
            link.classList.remove('active');
            if (href === '#' + sectionId) → add active;
            if (sectionId === 'home' && (href === 'index.html' || href === '#home')) → add active;
            if (sectionId === 'products' && href.indexOf('products.html') !== -1) → add active;
        });
    }
});
```

核心原则：**只在命中 section 时才改 active，不命中时什么都不动**（727eacd 初始版本模式）。

## 需要特殊映射的 section

5 个 section ID 与导航链接 href 的对应关系：

| Section ID | 导航 href | 匹配方式 |
|-----------|----------|---------|
| `home` | `index.html` | 显式判断（href 不是 `#home`） |
| `about` | `#about` | 通用 `href === '#about'` |
| `products` | `products.html?v=...` | 显式判断（href 不是 `#products`） |
| `news` | `#news` | 通用 `href === '#news'` |
| `contact` | `#contact` | 通用 `href === '#contact'` |

## 踩过的坑

1. **没发现 `section#home` 的存在** — banner 区域有 `id="home"`，它是第一个 section。`querySelectorAll('section[id]')` 选中了它，但导航链接没有 `href="#home"` 的链接 → 匹配失败 → 空白期。**教训：先查 HTML 结构再写匹配逻辑。**

2. **反复加 fallback 越改越乱** — 先后加了 `matched` 标志、`!matched` 回退、"先清空所有链接"等逻辑，都是因为没发现第一个 section 是 `#home`，试图用 fallback 填补不存在的 gap。**教训：找到根因再改，不要用 fallback 掩盖问题。**

3. **用 `href.indexOf(sectionId)` 模糊匹配** — 虽然能工作但不够精确，不如显式列出需要特殊处理的 section。**教训：精确匹配优先，特殊情况显式处理。**

4. **CSS transition 与 JS 频繁操作冲突** — 每次滚动都 `removeClass` + `addClass` 会导致 transition 动画反复触发。最终方案中，不命中就不操作，避免了这个问题。

## 关键 commit

- `727eacd` — 初始版本，最简 section 匹配模式（参考基准）
- `71bc820` — 增加了 products 特殊处理
