// 等待 DOM 加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 移动端菜单切换
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const nav = document.querySelector('.nav');
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            nav.classList.toggle('active');
            this.textContent = nav.classList.contains('active') ? '✕' : '☰';
        });
    }
    
    // 导航链接点击后关闭移动端菜单
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            nav.classList.remove('active');
            if (mobileMenuBtn) {
                mobileMenuBtn.textContent = '☰';
            }
            
            // 更新活动状态
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Banner 轮播功能
    const slides = document.querySelectorAll('.banner-slide');
    const dots = document.querySelectorAll('.banner-dot');
    const prevBtn = document.querySelector('.banner-prev');
    const nextBtn = document.querySelector('.banner-next');
    let currentSlide = 0;
    let slideInterval;
    
    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.classList.remove('active');
            dots[i].classList.remove('active');
        });
        
        slides[index].classList.add('active');
        dots[index].classList.add('active');
        currentSlide = index;
    }
    
    function nextSlide() {
        const next = (currentSlide + 1) % slides.length;
        showSlide(next);
    }
    
    function prevSlide() {
        const prev = (currentSlide - 1 + slides.length) % slides.length;
        showSlide(prev);
    }
    
    // 自动轮播
    function startSlideShow() {
        slideInterval = setInterval(nextSlide, 5000);
    }
    
    function stopSlideShow() {
        clearInterval(slideInterval);
    }
    
    // 事件绑定
    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            stopSlideShow();
            prevSlide();
            startSlideShow();
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            stopSlideShow();
            nextSlide();
            startSlideShow();
        });
    }
    
    dots.forEach((dot, index) => {
        dot.addEventListener('click', function() {
            stopSlideShow();
            showSlide(index);
            startSlideShow();
        });
    });
    
    // 启动自动轮播
    startSlideShow();
    
    // 数字增长动画
    const statNumbers = document.querySelectorAll('.stat-number');
    let animated = false;
    
    function animateNumbers() {
        if (animated) return;
        
        const statsSection = document.querySelector('.stats-section');
        if (!statsSection) return;
        
        const sectionTop = statsSection.offsetTop;
        const windowHeight = window.innerHeight;
        const scrollTop = window.pageYOffset;
        
        if (scrollTop + windowHeight > sectionTop + 100) {
            animated = true;
            
            statNumbers.forEach(num => {
                const target = parseInt(num.getAttribute('data-target'));
                const duration = 2000;
                const step = target / (duration / 16);
                let current = 0;
                
                const timer = setInterval(() => {
                    current += step;
                    if (current >= target) {
                        current = target;
                        clearInterval(timer);
                    }
                    num.textContent = Math.floor(current) + (target === 98 ? '%' : '+');
                }, 16);
            });
        }
    }
    
    // 滚动时触发数字动画
    window.addEventListener('scroll', animateNumbers);
    // 页面加载时也检查一次
    animateNumbers();
    
    // 平滑滚动
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = target.offsetTop - headerHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // 微信弹窗
    const wechatBtn = document.getElementById('wechatBtn');
    const wechatModal = document.getElementById('wechatModal');
    const closeModal = document.getElementById('closeModal');
    
    if (wechatBtn && wechatModal) {
        wechatBtn.addEventListener('click', function() {
            wechatModal.classList.add('active');
        });
    }
    
    if (closeModal && wechatModal) {
        closeModal.addEventListener('click', function() {
            wechatModal.classList.remove('active');
        });
    }
    
    // 点击弹窗外部关闭
    if (wechatModal) {
        wechatModal.addEventListener('click', function(e) {
            if (e.target === wechatModal) {
                wechatModal.classList.remove('active');
            }
        });
    }
    
    // 表单提交
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('感谢您的咨询！我们会尽快与您联系。');
            this.reset();
        });
    }
    
    // 滚动时导航栏效果
    let lastScrollTop = 0;
    const header = document.querySelector('.header');
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset;
        
        if (scrollTop > 100) {
            header.style.boxShadow = '0 2px 20px rgba(0,0,0,0.1)';
        } else {
            header.style.boxShadow = '0 2px 10px rgba(0,0,0,0.05)';
        }
        
        lastScrollTop = scrollTop;
    });
    
    // 滚动时更新导航活动状态
    const sections = document.querySelectorAll('section[id]');
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset;
        const headerHeight = header.offsetHeight;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop - headerHeight - 100;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');
            
            if (scrollTop >= sectionTop && scrollTop < sectionTop + sectionHeight) {
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === '#' + sectionId) {
                        link.classList.add('active');
                    }
                });
            }
        });
    });
});
