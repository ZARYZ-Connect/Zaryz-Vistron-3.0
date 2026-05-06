// VMS Professional Landing Page - Interactive Features
document.addEventListener('DOMContentLoaded', function () {
    initTimeGreeting();
    initButtonRippleEffect();
    initKeyboardShortcuts();
    initScrollAnimations();
    initKonamiCode();
    initConsoleEasterEgg();
    initFeatureHoverEffects();
    initProfilePlaceholder();
    initAnchorHandlers();
    injectDynamicStyles();
});

/* ================= TIME-BASED GREETING ================= */
function initTimeGreeting() {
    const badge = document.getElementById('heroBadge');
    if (!badge) return;

    const hour = new Date().getHours();
    const icon = badge.querySelector('i');
    const text = badge.querySelector('span');

    let greeting = 'Welcome';
    let iconClass = 'fa-star';

    if (hour >= 5 && hour < 12) {
        greeting = 'Good Morning';
        iconClass = 'fa-sun';
    } else if (hour >= 12 && hour < 17) {
        greeting = 'Good Afternoon';
        iconClass = 'fa-cloud-sun';
    } else if (hour >= 17 && hour < 22) {
        greeting = 'Good Evening';
        iconClass = 'fa-moon';
    }

    icon.className = `fas ${iconClass}`;
    text.textContent = `${greeting} - Enterprise-Grade Security`;
}

/* ================= BUTTON RIPPLE EFFECT ================= */
function initButtonRippleEffect() {
    document.querySelectorAll('.btn-primary-custom, .btn-secondary-custom')
        .forEach(button => {
            button.addEventListener('click', function (e) {
                const ripple = document.createElement('span');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;

                ripple.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.5);
                    left: ${x}px;
                    top: ${y}px;
                    transform: scale(0);
                    animation: ripple 0.6s ease-out;
                    pointer-events: none;
                `;

                this.style.position = 'relative';
                this.style.overflow = 'hidden';
                this.appendChild(ripple);

                setTimeout(() => ripple.remove(), 600);
            });
        });
}

/* ================= KEYBOARD SHORTCUTS ================= */
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function (e) {
        if (e.altKey && e.key.toLowerCase() === 'l') {
            e.preventDefault();
            const loginBtn = document.querySelector('a[href*="login"]');
            if (loginBtn) window.location.href = loginBtn.href;
        }

        if (e.altKey && e.key.toLowerCase() === 'd') {
            e.preventDefault();
            const dashBtn = document.querySelector('a[href*="dashboard"]');
            if (dashBtn) window.location.href = dashBtn.href;
        }
    });
}

/* ================= SCROLL ANIMATIONS ================= */
function initScrollAnimations() {
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.feature-card, .user-profile-card')
        .forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = '0.6s ease';
            observer.observe(el);
        });
}

/* ================= KONAMI CODE ================= */
function initKonamiCode() {
    const code = ['ArrowUp','ArrowUp','ArrowDown','ArrowDown','ArrowLeft','ArrowRight','ArrowLeft','ArrowRight','b','a'];
    let index = 0;

    document.addEventListener('keydown', e => {
        if (e.key === code[index]) {
            index++;
            if (index === code.length) {
                activateRainbowMode();
                index = 0;
            }
        } else index = 0;
    });
}

function activateRainbowMode() {
    document.body.style.animation = 'rainbowBackground 3s infinite';
    showNotification('🎉 Rainbow Mode!', 'You found the secret 🌈', 'rainbow');
    setTimeout(() => document.body.style.animation = '', 5000);
}

/* ================= NOTIFICATIONS ================= */
function showNotification(title, message, type = 'info') {
    const n = document.createElement('div');

    n.style.cssText = `
        position: fixed;
        top: 100px;
        right: 24px;
        background: ${type === 'rainbow'
            ? 'linear-gradient(135deg,#667eea,#764ba2,#f093fb)'
            : '#fff'};
        color: ${type === 'rainbow' ? '#fff' : '#111'};
        padding: 1.25rem 1.5rem;
        border-radius: 14px;
        box-shadow: 0 12px 40px rgba(0,0,0,.15);
        z-index: 9999;
        animation: slideInRight .5s ease;
    `;

    n.innerHTML = `
        <strong>${title}</strong>
        <div style="margin-top:6px; opacity:.9">${message}</div>
    `;

    document.body.appendChild(n);
    setTimeout(() => n.remove(), 5000);
}

/* ================= FEATURE HOVER ================= */
function initFeatureHoverEffects() {
    document.querySelectorAll('.feature-card').forEach(card => {
        const icon = card.querySelector('.feature-icon');
        card.onmouseenter = () => icon && (icon.style.transform = 'scale(1.1)');
        card.onmouseleave = () => icon && (icon.style.transform = '');
    });
}

/* ================= PROFILE PLACEHOLDER ================= */
function initProfilePlaceholder() {
    const p = document.querySelector('.profile-placeholder');
    if (!p) return;
    p.parentElement.onmouseenter = () => p.style.transform = 'rotate(360deg)';
    p.parentElement.onmouseleave = () => p.style.transform = '';
}

/* ================= ANCHOR HANDLER ================= */
function initAnchorHandlers() {
    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.onclick = e => {
            e.preventDefault();
            showNotification('Coming Soon', 'This feature will be available soon');
        };
    });
}

/* ================= DYNAMIC STYLES ================= */
function injectDynamicStyles() {
    const s = document.createElement('style');
    s.textContent = `
        @keyframes slideInRight {
            from { opacity:0; transform:translateX(300px) }
            to { opacity:1; transform:translateX(0) }
        }
        @keyframes rainbowBackground {
            from { filter:hue-rotate(0deg) }
            to { filter:hue-rotate(360deg) }
        }
    `;
    document.head.appendChild(s);
}

/* ================= CONSOLE EASTER EGG ================= */
function initConsoleEasterEgg() {
    console.log('%c🚀 VMS Platform Loaded', 'color:#6366f1;font-size:18px;font-weight:bold');
    console.log('%c⌨️ Alt+L Login | Alt+D Dashboard', 'color:#10b981');
}

