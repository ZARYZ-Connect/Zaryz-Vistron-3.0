// static/js/index-interactive.js

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all interactive features
    initTimeGreeting();
    initFirstVisitNotification();
    initButtonRippleEffect();
    initParallaxIcon();
    initKeyboardShortcuts();
    initKonamiCode();
    initHoverEnhancements();
});

// ==== TIME-BASED GREETING ====
function initTimeGreeting() {
    const greetingElement = document.querySelector('.greeting-text');
    if (!greetingElement) return;

    const hour = new Date().getHours();
    let greeting = '';
    let icon = '';

    if (hour >= 5 && hour < 12) {
        greeting = 'Good morning';
        icon = '☀️';
    } else if (hour >= 12 && hour < 17) {
        greeting = 'Good afternoon';
        icon = '🌤️';
    } else if (hour >= 17 && hour < 22) {
        greeting = 'Good evening';
        icon = '🌆';
    } else {
        greeting = 'Good night';
        icon = '🌙';
    }

    greetingElement.innerHTML = `<span class="me-2">${icon}</span>${greeting}!`;
}

// ==== FIRST VISIT NOTIFICATION ====
function initFirstVisitNotification() {
    // Check if user has visited before
    const hasVisited = localStorage.getItem('vms_visited');
    
    if (!hasVisited) {
        // Show welcome notification for first-time visitors
        setTimeout(() => {
            showWelcomeNotification();
            localStorage.setItem('vms_visited', 'true');
        }, 2000);
    }
}

function showWelcomeNotification() {
    const notification = document.createElement('div');
    notification.className = 'welcome-notification';
    notification.innerHTML = `
        <div class="notification-icon">
            <i class="fas fa-info-circle"></i>
        </div>
        <div class="notification-content">
            <div class="notification-title">Welcome to VMS! 👋</div>
            <div class="notification-message">
                First time here? Click "Register Visit" to get started. 
                Press <kbd>Alt + R</kbd> for quick access!
            </div>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 8 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.5s ease-out forwards';
        setTimeout(() => notification.remove(), 500);
    }, 8000);
}

// ==== BUTTON RIPPLE EFFECT ====
function initButtonRippleEffect() {
    const buttons = document.querySelectorAll('.btn-register, .btn-dashboard');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Remove existing ripple
            this.classList.remove('ripple');
            
            // Get click position relative to button
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Set CSS custom properties for ripple position
            this.style.setProperty('--ripple-x', `${x}px`);
            this.style.setProperty('--ripple-y', `${y}px`);
            
            // Add ripple class
            requestAnimationFrame(() => {
                this.classList.add('ripple');
            });
            
            // Create ripple element
            const ripple = document.createElement('span');
            ripple.style.position = 'absolute';
            ripple.style.width = '0';
            ripple.style.height = '0';
            ripple.style.borderRadius = '50%';
            ripple.style.background = 'rgba(255, 255, 255, 0.5)';
            ripple.style.transform = 'translate(-50%, -50%)';
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            ripple.style.pointerEvents = 'none';
            ripple.style.animation = 'rippleEffect 0.6s ease-out';
            
            this.appendChild(ripple);
            
            // Remove ripple element after animation
            setTimeout(() => ripple.remove(), 600);
        });
    });
}

// ==== PARALLAX ICON EFFECT ====
function initParallaxIcon() {
    const icon = document.querySelector('.main-icon');
    if (!icon) return;
    
    let ticking = false;
    
    window.addEventListener('scroll', function() {
        if (!ticking) {
            window.requestAnimationFrame(function() {
                const scrolled = window.pageYOffset;
                const parallaxSpeed = 0.3;
                
                // Move icon slower than scroll for depth effect
                icon.style.transform = `translateY(${scrolled * parallaxSpeed}px)`;
                
                ticking = false;
            });
            
            ticking = true;
        }
    });
    
    // Mouse parallax effect
    document.addEventListener('mousemove', function(e) {
        const container = document.querySelector('.floating-icon-container');
        if (!container) return;
        
        const rect = container.getBoundingClientRect();
        const containerCenterX = rect.left + rect.width / 2;
        const containerCenterY = rect.top + rect.height / 2;
        
        const deltaX = (e.clientX - containerCenterX) * 0.05;
        const deltaY = (e.clientY - containerCenterY) * 0.05;
        
        icon.style.transform = `translate(${deltaX}px, ${deltaY}px)`;
    });
    
    // Reset on mouse leave
    document.addEventListener('mouseleave', function() {
        icon.style.transform = '';
    });
}

// ==== KEYBOARD SHORTCUTS ====
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Alt + R: Quick register
        if (e.altKey && e.key.toLowerCase() === 'r') {
            e.preventDefault();
            const registerBtn = document.querySelector('.btn-register');
            if (registerBtn) {
                // Visual feedback
                registerBtn.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    registerBtn.style.transform = '';
                    window.location.href = registerBtn.getAttribute('href');
                }, 100);
            }
        }
        
        // Alt + D: Dashboard (if available)
        if (e.altKey && e.key.toLowerCase() === 'd') {
            e.preventDefault();
            const dashboardBtn = document.querySelector('.btn-dashboard');
            if (dashboardBtn) {
                dashboardBtn.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    dashboardBtn.style.transform = '';
                    window.location.href = dashboardBtn.getAttribute('href');
                }, 100);
            }
        }
    });
}

// ==== KONAMI CODE EASTER EGG ====
function initKonamiCode() {
    const konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
    let konamiIndex = 0;
    
    document.addEventListener('keydown', function(e) {
        if (e.key === konamiCode[konamiIndex]) {
            konamiIndex++;
            
            if (konamiIndex === konamiCode.length) {
                activateRainbowMode();
                konamiIndex = 0;
            }
        } else {
            konamiIndex = 0;
        }
    });
}

function activateRainbowMode() {
    const body = document.body;
    const card = document.querySelector('.index-card');
    const icon = document.querySelector('.main-icon');
    
    // Add rainbow class
    body.classList.add('rainbow-mode');
    if (card) card.classList.add('rainbow-mode');
    if (icon) icon.classList.add('rainbow-mode');
    
    // Show notification
    showRainbowNotification();
    
    // Play celebration sound (optional - would need audio file)
    // new Audio('/static/audio/celebration.mp3').play();
    
    // Remove after 5 seconds
    setTimeout(() => {
        body.classList.remove('rainbow-mode');
        if (card) card.classList.remove('rainbow-mode');
        if (icon) icon.classList.remove('rainbow-mode');
    }, 5000);
}

function showRainbowNotification() {
    const notification = document.createElement('div');
    notification.className = 'welcome-notification';
    notification.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)';
    notification.innerHTML = `
        <div class="notification-icon" style="background: rgba(255, 255, 255, 0.2);">
            <span style="font-size: 1.5rem;">🎉</span>
        </div>
        <div class="notification-content">
            <div class="notification-title" style="color: white;">Rainbow Mode Activated!</div>
            <div class="notification-message" style="color: rgba(255, 255, 255, 0.9);">
                You found the secret! Enjoy the colors! 🌈
            </div>
        </div>
        <button class="notification-close" style="color: white;" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.5s ease-out forwards';
        setTimeout(() => notification.remove(), 500);
    }, 5000);
}

// ==== HOVER ENHANCEMENTS ====
function initHoverEnhancements() {
    // Feature items rotation and scale
    const featureItems = document.querySelectorAll('.feature-item');
    featureItems.forEach(item => {
        const wrapper = item.querySelector('.feature-icon-wrapper');
        const icon = item.querySelector('.feature-icon');
        
        if (wrapper && icon) {
            wrapper.addEventListener('mouseenter', function() {
                this.style.transform = 'rotate(5deg) scale(1.1)';
                icon.style.transform = 'rotate(-5deg) scale(1.1)';
            });
            
            wrapper.addEventListener('mouseleave', function() {
                this.style.transform = '';
                icon.style.transform = '';
            });
        }
    });
    
    // Button hover effects with cursor tracking
    const buttons = document.querySelectorAll('.btn-register, .btn-dashboard');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function(e) {
            this.style.transform = 'translateY(-4px) scale(1.02)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
        
        // Subtle tilt effect based on mouse position
        button.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;
            
            this.style.transform = `translateY(-4px) scale(1.02) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        });
    });
    
    // Profile placeholder spin enhancement
    const profilePlaceholder = document.querySelector('.profile-placeholder');
    if (profilePlaceholder) {
        const profileCard = profilePlaceholder.closest('.user-profile-card');
        if (profileCard) {
            profileCard.addEventListener('mouseenter', function() {
                profilePlaceholder.style.transform = 'rotate(360deg)';
            });
            
            profileCard.addEventListener('mouseleave', function() {
                profilePlaceholder.style.transform = '';
            });
        }
    }
}

// ==== SCROLL REVEAL ANIMATIONS ====
function initScrollReveal() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = `fadeInUp 0.6s ease-out forwards`;
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements that should animate on scroll
    const elements = document.querySelectorAll('.feature-item, .user-profile-card');
    elements.forEach(el => observer.observe(el));
}

// ==== PERFORMANCE OPTIMIZATION ====
// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ==== AUTO-FOCUS REGISTER BUTTON ====
function initAutoFocus() {
    // Focus register button when page loads for accessibility
    setTimeout(() => {
        const registerBtn = document.querySelector('.btn-register');
        if (registerBtn) {
            registerBtn.focus();
        }
    }, 1000);
}

// ==== LOADING STATE ====
function initLoadingState() {
    // Remove any loading overlays
    const loader = document.querySelector('.page-loader');
    if (loader) {
        setTimeout(() => {
            loader.style.opacity = '0';
            setTimeout(() => loader.remove(), 300);
        }, 500);
    }
}

// Initialize all features
setTimeout(() => {
    initScrollReveal();
    initAutoFocus();
    initLoadingState();
}, 100);

// ==== UTILITY FUNCTIONS ====

// Create sparkle effect on icon click
document.querySelector('.main-icon')?.addEventListener('click', function(e) {
    createSparkles(e);
});

function createSparkles(e) {
    const colors = ['#6366f1', '#8b5cf6', '#10b981', '#f59e0b'];
    
    for (let i = 0; i < 12; i++) {
        const sparkle = document.createElement('div');
        sparkle.style.position = 'fixed';
        sparkle.style.left = e.clientX + 'px';
        sparkle.style.top = e.clientY + 'px';
        sparkle.style.width = '8px';
        sparkle.style.height = '8px';
        sparkle.style.borderRadius = '50%';
        sparkle.style.background = colors[Math.floor(Math.random() * colors.length)];
        sparkle.style.pointerEvents = 'none';
        sparkle.style.zIndex = '9999';
        
        const angle = (Math.PI * 2 * i) / 12;
        const velocity = 50 + Math.random() * 50;
        
        document.body.appendChild(sparkle);
        
        let x = 0;
        let y = 0;
        let opacity = 1;
        
        const animate = () => {
            x += Math.cos(angle) * 2;
            y += Math.sin(angle) * 2 - 1; // Gravity
            opacity -= 0.02;
            
            sparkle.style.transform = `translate(${x}px, ${y}px)`;
            sparkle.style.opacity = opacity;
            
            if (opacity > 0) {
                requestAnimationFrame(animate);
            } else {
                sparkle.remove();
            }
        };
        
        animate();
    }
}

// Console easter egg
console.log('%c🎉 Welcome to VMS! 🎉', 'color: #6366f1; font-size: 24px; font-weight: bold;');
console.log('%cTry the Konami Code: ↑ ↑ ↓ ↓ ← → ← → B A', 'color: #8b5cf6; font-size: 14px;');
console.log('%cKeyboard Shortcuts:\nAlt + R: Register Visit\nAlt + D: Dashboard', 'color: #10b981; font-size: 12px;');
