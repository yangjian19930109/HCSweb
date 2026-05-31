/**
 * product-detail.js — 产品详情页图片浏览
 */
(function () {
    'use strict';

    function initProductDetail() {
        var mainImg = document.getElementById('mainImg');
        var thumbs = document.querySelectorAll('.thumb');
        if (!mainImg || thumbs.length === 0) return;

        var currentIndex = 0;

        // 缩略图悬停切换主图
        thumbs.forEach(function (thumb, idx) {
            thumb.addEventListener('mouseenter', function () {
                switchTo(idx);
            });
        });

        function switchTo(idx) {
            mainImg.src = thumbs[idx].src;
            thumbs.forEach(function (t) { t.classList.remove('active'); });
            thumbs[idx].classList.add('active');
            currentIndex = idx;
        }

        // 前后翻按钮
        var prevBtn = document.querySelector('.img-prev');
        var nextBtn = document.querySelector('.img-next');

        if (prevBtn) {
            prevBtn.addEventListener('click', function () {
                var newIdx = (currentIndex - 1 + thumbs.length) % thumbs.length;
                switchTo(newIdx);
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', function () {
                var newIdx = (currentIndex + 1) % thumbs.length;
                switchTo(newIdx);
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initProductDetail);
    } else {
        initProductDetail();
    }
})();
