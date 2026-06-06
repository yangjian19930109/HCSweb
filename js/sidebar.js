/**
 * sidebar.js — 侧边栏 Tab 切换与 URL hash 同步
 */
(function () {
    'use strict';

    function initSidebar() {
        var sidebarItems = document.querySelectorAll('.sidebar-nav-item[data-tab]');
        var tabPanels = document.querySelectorAll('.product-tab-panel');
        if (sidebarItems.length === 0) return;

        // 点击切换
        sidebarItems.forEach(function (item) {
            item.addEventListener('click', function (e) {
                // 如果子菜单项有链接，不阻止跳转
                if (e.target.closest('.sidebar-sub-item a') || e.target.closest('.sidebar-sub-item[onclick]')) {
                    return;
                }
                var tabId = item.getAttribute('data-tab');
                if (!tabId) return;

                // 更新高亮
                sidebarItems.forEach(function (i) { i.classList.remove('active'); });
                item.classList.add('active');

                // 切换面板
                if (tabPanels.length > 0) {
                    tabPanels.forEach(function (panel) {
                        panel.classList.remove('active');
                        if (panel.id === 'tab-' + tabId) {
                            panel.classList.add('active');
                        }
                    });
                    // 更新 URL hash
                    history.replaceState(null, '', '#' + tabId);
                } else {
                    // 非产品中心页（子类目页/详情页），跳转到产品中心对应 tab
                    window.location.href = 'products.html#tab-' + tabId;
                }
            });
        });

        function switchToTab(hash) {
            var targetPanel = document.getElementById('tab-' + hash);
            var targetItem = document.querySelector('.sidebar-nav-item[data-tab="' + hash + '"]');
            if (targetPanel && tabPanels.length > 0) {
                sidebarItems.forEach(function (i) { i.classList.remove('active'); });
                if (targetItem) targetItem.classList.add('active');
                tabPanels.forEach(function (panel) {
                    panel.classList.remove('active');
                    if (panel.id === 'tab-' + hash) {
                        panel.classList.add('active');
                    }
                });
            }
        }

        // 页面加载时检查 URL hash
        var hash = window.location.hash.replace('#', '');
        if (hash) {
            switchToTab(hash);
        }

        // 监听 hash 变化（导航下拉、浏览器前进后退等）
        window.addEventListener('hashchange', function () {
            var newHash = window.location.hash.replace('#', '');
            if (newHash) {
                switchToTab(newHash);
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSidebar);
    } else {
        initSidebar();
    }
})();
