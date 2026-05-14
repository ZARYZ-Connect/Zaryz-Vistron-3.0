// static/js/security.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all security module features
    initStatCards();
    initTableAnimations();
    initQuickActions();
    initBadgeLookup();
});

// Stat Card Interactions
function initStatCards() {
    const statCards = document.querySelectorAll('.stat-card');
    
    statCards.forEach((card, index) => {
        // Stagger animation
        card.style.animationDelay = `${index * 0.1}s`;
        
        // Hover effect enhancement
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-12px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Table Row Animations
function initTableAnimations() {
    const tableRows = document.querySelectorAll('.modern-table tbody tr');
    
    tableRows.forEach((row, index) => {
        // Stagger animation
        row.style.opacity = '0';
        row.style.animation = `slideUp 0.4s ease-out forwards`;
        row.style.animationDelay = `${index * 0.05}s`;
        
        // Enhanced hover
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(99, 102, 241, 0.04)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });
}

// Quick Action Buttons
function initQuickActions() {
    const actionButtons = document.querySelectorAll('.btn-view, .btn-primary-modern, .btn-success-modern, .btn-warning-modern');
    
    actionButtons.forEach(button => {
        // Magnetic effect logic
        button.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            
            this.style.transform = `translate(${x * 0.3}px, ${y * 0.3}px) scale(1.05)`;
            this.style.boxShadow = `${-x * 0.2}px ${-y * 0.2}px 25px rgba(0,0,0,0.2)`;
            
            const icon = this.querySelector('i');
            if (icon) {
                icon.style.transform = `translate(${x * 0.1}px, ${y * 0.1}px)`;
            }
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
            const icon = this.querySelector('i');
            if (icon) {
                icon.style.transform = '';
            }
        });
    });
}

// Badge Lookup Enhancement
function initBadgeLookup() {
    const lookupInput = document.querySelector('.lookup-input');
    const lookupForm = document.querySelector('.lookup-form form');
    
    if (lookupInput) {
        // Focus animation
        lookupInput.addEventListener('focus', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 8px 20px rgba(99, 102, 241, 0.15)';
        });
        
        lookupInput.addEventListener('blur', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '';
        });
        
        // Auto-uppercase badge ID
        lookupInput.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
    }
    
    if (lookupForm) {
        lookupForm.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Searching...';
                submitBtn.disabled = true;
            }
        });
    }
}

// Auto-refresh dashboard every 30 seconds (optional)
function enableAutoRefresh() {
    const isDashboard = document.querySelector('.security-dashboard');
    if (isDashboard) {
        setInterval(() => {
            // Only refresh if user hasn't interacted recently
            const lastActivity = Date.now() - (window.lastActivityTime || Date.now());
            if (lastActivity > 60000) { // 1 minute
                location.reload();
            }
        }, 30000); // 30 seconds
    }
    
    // Track user activity
    document.addEventListener('mousemove', () => {
        window.lastActivityTime = Date.now();
    });
    document.addEventListener('keydown', () => {
        window.lastActivityTime = Date.now();
    });
}

// Status badge color animation
function animateStatusBadges() {
    const badges = document.querySelectorAll('.status-badge');
    badges.forEach((badge, index) => {
        badge.style.animation = `fadeIn 0.5s ease-out forwards`;
        badge.style.animationDelay = `${index * 0.1}s`;
    });
}

// Call animations
animateStatusBadges();