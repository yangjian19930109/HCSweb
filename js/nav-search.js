/**
 * nav-search.js — 导航栏搜索功能
 * 依赖: Fuse.js (CDN), data/products.js (PRODUCTS_DATA + doSearch + initFuse)
 */
(function () {
    'use strict';

    function initNavSearch() {
        var input = document.getElementById('nav-search-input');
        var results = document.getElementById('nav-search-results');
        if (!input || !results) return;

        // 初始化 Fuse (如果已加载)
        if (typeof Fuse !== 'undefined' && typeof initFuse === 'function') {
            initFuse();
        }

        // 输入搜索
        input.addEventListener('input', function () {
            var q = input.value.trim();
            if (!q) {
                results.innerHTML = '<div class="ns-hint">输入关键词搜索...</div>';
                results.classList.add('visible');
                return;
            }
            var hits;
            if (typeof doSearch === 'function') {
                hits = doSearch(q);
            } else {
                hits = (window.PRODUCTS_DATA || []).filter(function (p) {
                    return p.title.indexOf(q) >= 0 || p.desc.indexOf(q) >= 0;
                }).slice(0, 10);
            }
            if (hits.length === 0) {
                results.innerHTML = '<div class="ns-empty">未找到相关结果</div>';
                results.classList.add('visible');
                return;
            }
            results.innerHTML = hits.map(function (item) {
                var d = item.item || item;
                return '<a href="' + (d.url || '#') + '" class="ns-item">' +
                    '<span class="ns-cat">' + (d.subCat || '') + '</span>' +
                    '<span class="ns-title">' + (d.title || '') + '</span>' +
                    '<span class="ns-desc">' + (d.desc || '') + '</span></a>';
            }).join('');
            results.classList.add('visible');
        });

        // 聚焦时显示提示
        input.addEventListener('focus', function () {
            if (!input.value.trim() && !results.innerHTML) {
                results.innerHTML = '<div class="ns-hint">输入关键词搜索...</div>';
            }
            results.classList.add('visible');
        });

        // 点击外部关闭
        document.addEventListener('click', function (e) {
            if (!e.target.closest('.nav-search')) {
                results.classList.remove('visible');
            }
        });

        // Escape 关闭
        input.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                results.classList.remove('visible');
                input.blur();
                // 移动端同时收起搜索条
                var box = document.getElementById('nav-search-box');
                if (box) box.classList.remove('active');
            }
        });

        // 移动端搜索按钮切换
        var searchBtn = document.getElementById('mobile-search-btn');
        var searchBox = document.getElementById('nav-search-box');
        if (searchBtn && searchBox) {
            searchBtn.addEventListener('click', function (e) {
                e.stopPropagation();
                searchBox.classList.toggle('active');
                if (searchBox.classList.contains('active')) {
                    input.focus();
                }
            });
            // 点击页面其他区域关闭
            document.addEventListener('click', function (e) {
                if (!e.target.closest('.nav-search') && !e.target.closest('.mobile-search-btn')) {
                    searchBox.classList.remove('active');
                }
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNavSearch);
    } else {
        initNavSearch();
    }
})();
