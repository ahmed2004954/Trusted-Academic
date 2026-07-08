document.addEventListener('DOMContentLoaded', function () {
    document.documentElement.classList.add('js');

    // ==========================================================================
    // Form Submission & Disabling Buttons
    // ==========================================================================
    const forms = document.querySelectorAll('form');
    forms.forEach(function (form) {
        form.addEventListener('submit', function () {
            const submitters = form.querySelectorAll('button[type="submit"], input[type="submit"]');
            submitters.forEach(function (button) {
                if (button.dataset.noDisable === 'true') {
                    return;
                }
                button.disabled = true;
                if (button.tagName === 'BUTTON' && button.textContent.trim()) {
                    button.dataset.originalText = button.textContent;
                    button.textContent = 'جاري الإرسال...';
                }
            });
        });
    });

    // ==========================================================================
    // IntersectionObserver for Reveal Animations
    // ==========================================================================
    const revealElements = document.querySelectorAll('.reveal');
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    if (prefersReducedMotion.matches || typeof IntersectionObserver === 'undefined') {
        revealElements.forEach(function (element) {
            element.classList.add('is-visible');
        });
    } else if (revealElements.length > 0) {
        const revealObserver = new IntersectionObserver(function (entries, observer) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.15,
            rootMargin: '0px 0px -10% 0px',
        });

        revealElements.forEach(function (element) {
            revealObserver.observe(element);
        });
    }

    // ==========================================================================
    // Toast Dismissal System
    // ==========================================================================
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(function (toast) {
        const closeBtn = toast.querySelector('.toast-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function () {
                dismissToast(toast);
            });
        }
        // Auto dismiss after 5s
        setTimeout(function () {
            dismissToast(toast);
        }, 5000);
    });

    function dismissToast(toast) {
        if (!toast.parentNode) return;
        toast.classList.add('toast-hiding');
        setTimeout(function () {
            toast.remove();
        }, 300);
    }

    // ==========================================================================
    // Sticky Header Reveal Scroll Logic
    // ==========================================================================
    let lastScrollY = window.scrollY;
    const header = document.getElementById('site-header');
    if (header) {
        window.addEventListener('scroll', function () {
            const currentScrollY = window.scrollY;
            if (currentScrollY > 70 && currentScrollY > lastScrollY) {
                header.classList.add('header-hidden');
            } else {
                header.classList.remove('header-hidden');
            }
            lastScrollY = currentScrollY;
        }, { passive: true });
    }

    // ==========================================================================
    // User Profile Dropdown Toggle
    // ==========================================================================
    const dropdownToggle = document.querySelector('.user-dropdown-toggle');
    const dropdownMenu = document.querySelector('.user-dropdown-menu');
    if (dropdownToggle && dropdownMenu) {
        dropdownToggle.addEventListener('click', function (e) {
            e.stopPropagation();
            const isExpanded = dropdownToggle.getAttribute('aria-expanded') === 'true';
            dropdownToggle.setAttribute('aria-expanded', !isExpanded);
            dropdownMenu.classList.toggle('show');
        });

        // Click outside to close dropdown
        document.addEventListener('click', function (e) {
            if (!dropdownToggle.contains(e.target) && !dropdownMenu.contains(e.target)) {
                dropdownToggle.setAttribute('aria-expanded', 'false');
                dropdownMenu.classList.remove('show');
            }
        });

        // Escape key to close dropdown
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                dropdownToggle.setAttribute('aria-expanded', 'false');
                dropdownMenu.classList.remove('show');
            }
        });
    }

    // ==========================================================================
    // Off-Canvas Mobile Navigation Drawer
    // ==========================================================================
    const burgerMenuBtn = document.getElementById('burgerMenuButton');
    const drawerCloseBtn = document.getElementById('drawerCloseButton');
    const drawerOverlay = document.getElementById('drawerOverlay');
    const mobileDrawer = document.getElementById('mobileDrawer');

    if (burgerMenuBtn && mobileDrawer) {
        function openDrawer() {
            mobileDrawer.classList.add('show');
            mobileDrawer.setAttribute('aria-hidden', 'false');
            burgerMenuBtn.setAttribute('aria-expanded', 'true');
            document.body.style.overflow = 'hidden';
        }

        function closeDrawer() {
            mobileDrawer.classList.remove('show');
            mobileDrawer.setAttribute('aria-hidden', 'true');
            burgerMenuBtn.setAttribute('aria-expanded', 'false');
            document.body.style.overflow = '';
        }

        burgerMenuBtn.addEventListener('click', openDrawer);
        if (drawerCloseBtn) drawerCloseBtn.addEventListener('click', closeDrawer);
        if (drawerOverlay) drawerOverlay.addEventListener('click', closeDrawer);

        // Escape key to close drawer
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                closeDrawer();
            }
        });
    }

    // ==========================================================================
    // Dark / Light Theme Toggler (Forest Night)
    // ==========================================================================
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const mobileThemeToggleBtn = document.getElementById('mobileThemeToggleBtn');

    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const isDarkInitial = savedTheme === 'dark' || (!savedTheme && systemPrefersDark);

    if (isDarkInitial) {
        document.documentElement.classList.add('dark-theme');
        updateThemeIcons(true);
    } else {
        document.documentElement.classList.remove('dark-theme');
        updateThemeIcons(false);
    }

    function updateThemeIcons(isDark) {
        const iconName = isDark ? 'dark_mode' : 'light_mode';
        if (themeToggleBtn) {
            const iconSpan = themeToggleBtn.querySelector('.material-symbols-outlined');
            if (iconSpan) iconSpan.textContent = iconName;
        }
        if (mobileThemeToggleBtn) {
            const iconSpan = mobileThemeToggleBtn.querySelector('.material-symbols-outlined');
            if (iconSpan) iconSpan.textContent = iconName;
        }
    }

    function toggleTheme() {
        const isDark = document.documentElement.classList.toggle('dark-theme');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        updateThemeIcons(isDark);
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }
    if (mobileThemeToggleBtn) {
        mobileThemeToggleBtn.addEventListener('click', toggleTheme);
    }
});
