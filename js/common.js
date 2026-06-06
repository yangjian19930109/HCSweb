/**
 * common.js — 华创生电机网站通用脚本
 * 移动菜单、平滑滚动、导航 active、微信弹窗
 */
(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        initMobileMenu();
        initSmoothScroll();
        initNavActive();
        initWechatModal();
        initContactForm();
    });

    /* ========== 移动端菜单 ========== */
    function initMobileMenu() {
        var btn = document.querySelector('.mobile-menu-btn');
        var nav = document.querySelector('.nav');
        if (!btn || !nav) return;

        btn.addEventListener('click', function () {
            nav.classList.toggle('active');
            btn.textContent = nav.classList.contains('active') ? '✕' : '☰';
        });

        // 点击导航链接后关闭菜单
        var links = nav.querySelectorAll('.nav-link');
        links.forEach(function (link) {
            link.addEventListener('click', function (e) {
                // 移动端下拉菜单切换：不关闭菜单，交给下面的 dropdown handler 处理
                if (window.innerWidth <= 768 && link.closest('.nav-dropdown')) {
                    return;
                }
                nav.classList.remove('active');
                btn.textContent = '☰';
            });
        });

        // 移动端下拉菜单点击展开
        var dropdown = nav.querySelector('.nav-dropdown');
        var dropdownMenu = nav.querySelector('.dropdown-menu');
        if (dropdown && dropdownMenu) {
            var dropdownLink = dropdown.querySelector('.nav-link');
            if (dropdownLink) {
                dropdownLink.addEventListener('click', function (e) {
                    if (window.innerWidth <= 768) {
                        e.preventDefault();
                        dropdownMenu.classList.toggle('active');
                    }
                });
            }
        }
    }

    /* ========== 平滑滚动 ========== */
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
            anchor.addEventListener('click', function (e) {
                var targetId = this.getAttribute('href');
                if (targetId === '#') return;
                e.preventDefault();
                var target = document.querySelector(targetId);
                if (target) {
                    var header = document.querySelector('.header');
                    var headerHeight = header ? header.offsetHeight : 80;
                    var targetPosition = target.offsetTop - headerHeight;
                    window.scrollTo({ top: targetPosition, behavior: 'smooth' });
                }
            });
        });
    }

    /* ========== 导航 active 状态 ========== */
    function initNavActive() {
        updateNavActive();
        window.addEventListener('hashchange', updateNavActive);
        window.addEventListener('scroll', updateNavOnScroll);
    }

    function updateNavActive() {
        var hash = window.location.hash;
        var navLinks = document.querySelectorAll('.nav-link');
        var currentUrl = window.location.href.split('/').pop().split('?')[0].split('#')[0];

        navLinks.forEach(function (link) {
            link.classList.remove('active');
            var href = link.getAttribute('href') || '';

            // 先按页面 URL 匹配（不受 hash 影响）
            if (currentUrl === 'index.html' || currentUrl === '') {
                if (href === 'index.html' || href === '#home') {
                    link.classList.add('active');
                }
            } else if (currentUrl.startsWith('product-') || currentUrl.startsWith('other-') ||
                       currentUrl.startsWith('throttle-') || currentUrl.startsWith('turbo-') ||
                       currentUrl === 'products.html') {
                if (href.includes('products.html')) {
                    link.classList.add('active');
                }
            }

            // hash 精确匹配（首页区块导航）
            if (hash && (href.endsWith(hash) || href === hash)) {
                link.classList.add('active');
            }
        });
    }

    function updateNavOnScroll() {
        var scrollTop = window.pageYOffset;
        var header = document.querySelector('.header');
        var headerHeight = header ? header.offsetHeight : 80;
        var sections = document.querySelectorAll('section[id]');
        var navLinks = document.querySelectorAll('.nav-link');

        // 页面无区块，交由 updateNavActive 处理
        if (sections.length === 0) return;

        sections.forEach(function (section) {
            var sectionTop = section.offsetTop - headerHeight - 100;
            var sectionHeight = section.offsetHeight;
            var sectionId = section.getAttribute('id');

            if (scrollTop >= sectionTop && scrollTop < sectionTop + sectionHeight) {
                navLinks.forEach(function (link) {
                    link.classList.remove('active');
                    var href = link.getAttribute('href') || '';
                    if (href === '#' + sectionId) {
                        link.classList.add('active');
                    }
                    // #home 区块（banner）→ 首页导航链接
                    if (sectionId === 'home' && (href === 'index.html' || href === '#home')) {
                        link.classList.add('active');
                    }
                    // #products 区块 → 产品中心导航链接
                    if (sectionId === 'products' && href.indexOf('products.html') !== -1) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }

    /* ========== 微信弹窗 ========== */
    function initWechatModal() {
        var wechatBtn = document.getElementById('wechatBtn');
        var wechatModal = document.getElementById('wechatModal');
        var closeModal = document.getElementById('closeModal');

        if (wechatBtn && wechatModal) {
            wechatBtn.addEventListener('click', function () {
                wechatModal.classList.add('active');
            });
        }

        if (closeModal && wechatModal) {
            closeModal.addEventListener('click', function () {
                wechatModal.classList.remove('active');
            });
        }

        if (wechatModal) {
            wechatModal.addEventListener('click', function (e) {
                if (e.target === wechatModal) {
                    wechatModal.classList.remove('active');
                }
            });
        }
    }

    /* ========== 联系表单 ========== */
    function initContactForm() {
        var form = document.getElementById('contactForm');
        if (form) {
            form.addEventListener('submit', function (e) {
                e.preventDefault();
                alert('感谢您的咨询！我们会尽快与您联系。');
                form.reset();
            });
        }
    }
})();
