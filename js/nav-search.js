/**
 * nav-search.js — 导航栏搜索功能
 * 通过后端 API 搜索，不暴露完整产品数据
 */
(function () {
    'use strict';

    function initNavSearch() {
        var input = document.getElementById('nav-search-input');
        var results = document.getElementById('nav-search-results');
        if (!input || !results) return;

        var debounceTimer = null;
        var lastQuery = '';

        function searchAPI(q) {
            // 清空旧结果
            if (!q) {
                results.innerHTML = '<div class="ns-hint">输入关键词搜索...</div>';
                results.classList.add('visible');
                return;
            }

            results.innerHTML = '<div class="ns-hint">搜索中...</div>';
            results.classList.add('visible');

            fetch('/api/search?q=' + encodeURIComponent(q))
                .then(function (r) { return r.json(); })
                .then(function (hits) {
                    // 确保结果对应最新的查询
                    if (q !== lastQuery) return;
                    if (!hits || hits.length === 0) {
                        results.innerHTML = '<div class="ns-empty">未找到相关结果</div>';
                        results.classList.add('visible');
                        return;
                    }
                    results.innerHTML = hits.map(function (item) {
                        return '<a href="' + (item.url || '#') + '" class="ns-item">' +
                            '<span class="ns-cat">' + (item.subCat || '') + '</span>' +
                            '<span class="ns-title">' + (item.title || '') + '</span>' +
                            '<span class="ns-desc">' + (item.desc || '') + '</span></a>';
                    }).join('');
                    results.classList.add('visible');
                })
                .catch(function () {
                    if (q === lastQuery) {
                        results.innerHTML = '<div class="ns-empty">搜索失败，请重试</div>';
                        results.classList.add('visible');
                    }
                });
        }

        // 输入搜索（300ms 防抖）
        input.addEventListener('input', function () {
            var q = input.value.trim();
            lastQuery = q;
            if (debounceTimer) clearTimeout(debounceTimer);
            if (!q) {
                searchAPI('');
            } else {
                debounceTimer = setTimeout(function () { searchAPI(q); }, 300);
            }
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
