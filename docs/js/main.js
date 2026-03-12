(function() {
    'use strict';

    const DOM = {
        nav: document.getElementById('nav'),
        navToggle: document.getElementById('navToggle'),
        navMenu: document.getElementById('navMenu'),
        backToTop: document.getElementById('backToTop'),
        toast: document.getElementById('toast'),
        downloadBtns: document.querySelectorAll('.download-btn'),
        copyBtns: document.querySelectorAll('.copy-btn'),
        statNumbers: document.querySelectorAll('.stat-card__number'),
        dropdownItems: document.querySelectorAll('.nav__item--dropdown')
    };

    const Config = {
        scrollThreshold: 500,
        animationDuration: 2000,
        toastDuration: 3000,
        downloadUrl: 'https://github.com/badhope/python-exercise-9999/archive/refs/heads/main.zip'
    };

    function initNavigation() {
        if (!DOM.navToggle || !DOM.navMenu) return;

        DOM.navToggle.addEventListener('click', function() {
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            this.setAttribute('aria-expanded', !isExpanded);
            DOM.navMenu.classList.toggle('active');
            
            this.querySelectorAll('.nav__toggle-bar').forEach((bar, index) => {
                if (!isExpanded) {
                    if (index === 0) bar.style.transform = 'rotate(45deg) translate(5px, 5px)';
                    if (index === 1) bar.style.opacity = '0';
                    if (index === 2) bar.style.transform = 'rotate(-45deg) translate(5px, -5px)';
                } else {
                    bar.style.transform = '';
                    bar.style.opacity = '';
                }
            });
        });

        DOM.dropdownItems.forEach(item => {
            const link = item.querySelector('.nav__link--dropdown');
            if (link) {
                link.addEventListener('click', function(e) {
                    if (window.innerWidth <= 768) {
                        e.preventDefault();
                        item.classList.toggle('active');
                        const isExpanded = this.getAttribute('aria-expanded') === 'true';
                        this.setAttribute('aria-expanded', !isExpanded);
                    }
                });
            }
        });

        document.addEventListener('click', function(e) {
            if (!e.target.closest('.nav') && DOM.navMenu.classList.contains('active')) {
                DOM.navMenu.classList.remove('active');
                DOM.navToggle.setAttribute('aria-expanded', 'false');
                DOM.navToggle.querySelectorAll('.nav__toggle-bar').forEach(bar => {
                    bar.style.transform = '';
                    bar.style.opacity = '';
                });
            }
        });

        document.querySelectorAll('.nav__link[href^="#"]').forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    DOM.navMenu.classList.remove('active');
                    DOM.navToggle.setAttribute('aria-expanded', 'false');
                }
            });
        });
    }

    function initBackToTop() {
        if (!DOM.backToTop) return;

        let ticking = false;

        function updateBackToTop() {
            const scrollY = window.scrollY || window.pageYOffset;
            
            if (scrollY > Config.scrollThreshold) {
                DOM.backToTop.hidden = false;
            } else {
                DOM.backToTop.hidden = true;
            }
            
            ticking = false;
        }

        window.addEventListener('scroll', function() {
            if (!ticking) {
                requestAnimationFrame(updateBackToTop);
                ticking = true;
            }
        }, { passive: true });

        DOM.backToTop.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });

        updateBackToTop();
    }

    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href === '#') return;
                
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    
                    const navHeight = DOM.nav ? DOM.nav.offsetHeight : 0;
                    const targetPosition = target.getBoundingClientRect().top + window.scrollY - navHeight - 20;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });

                    if (history.pushState) {
                        history.pushState(null, null, href);
                    }
                }
            });
        });
    }

    function initDownload() {
        DOM.downloadBtns.forEach(btn => {
            btn.addEventListener('click', async function() {
                const downloadType = this.dataset.download;
                const card = this.closest('.download-card');
                const progress = card.querySelector('.download-card__progress');
                const progressBar = card.querySelector('.download-card__progress-bar');
                const status = card.querySelector('.download-card__status');
                
                this.disabled = true;
                
                if (progress) progress.hidden = false;
                if (status) {
                    status.hidden = false;
                    status.textContent = '准备下载...';
                }

                try {
                    if (downloadType === 'zip') {
                        simulateProgress(progressBar);
                        
                        const link = document.createElement('a');
                        link.href = Config.downloadUrl;
                        link.download = 'python-exercise-9999-main.zip';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        
                        if (status) status.textContent = '下载已开始！';
                        showToast('下载已开始，请检查您的下载文件夹');
                    }
                } catch (error) {
                    if (status) status.textContent = '下载失败，请重试';
                    showToast('下载失败，请稍后重试');
                    console.error('Download error:', error);
                } finally {
                    setTimeout(() => {
                        this.disabled = false;
                        if (progress) progress.hidden = true;
                        if (progressBar) progressBar.style.width = '0%';
                    }, 2000);
                }
            });
        });
    }

    function simulateProgress(progressBar) {
        if (!progressBar) return;
        
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 20;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
            }
            progressBar.style.width = progress + '%';
        }, 100);
    }

    function initCopy() {
        DOM.copyBtns.forEach(btn => {
            btn.addEventListener('click', async function() {
                const targetId = this.dataset.copy;
                const target = document.getElementById(targetId);
                
                if (target) {
                    try {
                        await navigator.clipboard.writeText(target.textContent);
                        
                        const originalHTML = this.innerHTML;
                        this.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>';
                        this.style.color = 'var(--color-success)';
                        
                        showToast('已复制到剪贴板');
                        
                        setTimeout(() => {
                            this.innerHTML = originalHTML;
                            this.style.color = '';
                        }, 2000);
                    } catch (error) {
                        fallbackCopy(target.textContent);
                        showToast('已复制到剪贴板');
                    }
                }
            });
        });
    }

    function fallbackCopy(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.left = '-9999px';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
    }

    function initStatsAnimation() {
        if (!DOM.statNumbers.length) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateNumber(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.5
        });

        DOM.statNumbers.forEach(el => observer.observe(el));
    }

    function animateNumber(element) {
        const target = parseInt(element.dataset.count, 10);
        const duration = Config.animationDuration;
        const startTime = performance.now();
        const suffix = element.nextElementSibling?.classList.contains('stat-card__suffix') ? '%' : '';

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const current = Math.floor(target * easeOutQuart);
            
            element.textContent = current;
            
            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                element.textContent = target;
            }
        }

        requestAnimationFrame(update);
    }

    function showToast(message) {
        if (!DOM.toast) return;
        
        const messageEl = DOM.toast.querySelector('.toast__message');
        if (messageEl) {
            messageEl.textContent = message;
        }
        
        DOM.toast.hidden = false;
        
        setTimeout(() => {
            DOM.toast.hidden = true;
        }, Config.toastDuration);
    }

    function initNavScroll() {
        if (!DOM.nav) return;

        let lastScrollY = 0;
        let ticking = false;

        function updateNav() {
            const scrollY = window.scrollY || window.pageYOffset;
            
            if (scrollY > 100) {
                DOM.nav.style.boxShadow = 'var(--shadow-md)';
            } else {
                DOM.nav.style.boxShadow = 'none';
            }
            
            lastScrollY = scrollY;
            ticking = false;
        }

        window.addEventListener('scroll', function() {
            if (!ticking) {
                requestAnimationFrame(updateNav);
                ticking = true;
            }
        }, { passive: true });
    }

    function initKeyboardNavigation() {
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                if (DOM.navMenu && DOM.navMenu.classList.contains('active')) {
                    DOM.navMenu.classList.remove('active');
                    DOM.navToggle.setAttribute('aria-expanded', 'false');
                    DOM.navToggle.focus();
                }
            }
        });

        DOM.dropdownItems.forEach(item => {
            const dropdown = item.querySelector('.nav__dropdown');
            const links = dropdown?.querySelectorAll('.nav__dropdown-link');
            
            if (links?.length) {
                const firstLink = links[0];
                const lastLink = links[links.length - 1];
                
                lastLink.addEventListener('keydown', function(e) {
                    if (e.key === 'Tab' && !e.shiftKey) {
                        item.querySelector('.nav__link--dropdown')?.focus();
                    }
                });
                
                firstLink.addEventListener('keydown', function(e) {
                    if (e.key === 'Tab' && e.shiftKey) {
                        item.querySelector('.nav__link--dropdown')?.focus();
                    }
                });
            }
        });
    }

    function init() {
        initNavigation();
        initBackToTop();
        initSmoothScroll();
        initDownload();
        initCopy();
        initStatsAnimation();
        initNavScroll();
        initKeyboardNavigation();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
