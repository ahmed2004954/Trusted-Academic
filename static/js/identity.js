function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    if (!menu) return;
    if (menu.classList.contains('hidden')) {
        menu.classList.remove('hidden');
        setTimeout(() => {
            const panel = menu.querySelector('.transform');
            if (panel) panel.classList.remove('translate-x-full');
        }, 10);
    } else {
        const panel = menu.querySelector('.transform');
        if (panel) panel.classList.add('translate-x-full');
        setTimeout(() => menu.classList.add('hidden'), 300);
    }
}

document.addEventListener('click', function (e) {
    const menu = document.getElementById('mobile-menu');
    if (!menu || menu.classList.contains('hidden')) return;
    if (menu.contains(e.target)) return;
    const toggle = e.target.closest && e.target.closest('[onclick*="toggleMobileMenu"]');
    if (toggle) return;
    const panel = menu.querySelector('.transform');
    if (panel) panel.classList.add('translate-x-full');
    setTimeout(() => menu.classList.add('hidden'), 300);
});

document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        const menu = document.getElementById('mobile-menu');
        if (menu && !menu.classList.contains('hidden')) {
            const panel = menu.querySelector('.transform');
            if (panel) panel.classList.add('translate-x-full');
            setTimeout(() => menu.classList.add('hidden'), 300);
        }
    }
});
