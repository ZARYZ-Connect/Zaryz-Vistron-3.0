// static/js/delete-confirm.js - Ultra Modern & Compact
(function() {
    'use strict';

    const elements = {
        form: document.getElementById('deleteForm'),
        deleteBtn: document.querySelector('.btn-delete'),
        cancelBtn: document.querySelector('.btn-cancel'),
        card: document.querySelector('.delete-card')
    };

    if (!elements.form || !elements.deleteBtn) return;

    // Initialize
    init();

    function init() {
        setupFormHandler();
        setupKeyboardShortcuts();
        setupAccessibility();
        autoScroll();
        preventDoubleClick();
    }

    // Form submission with loading state
    function setupFormHandler() {
        elements.form.addEventListener('submit', function(e) {
            if (elements.deleteBtn.disabled) {
                e.preventDefault();
                return;
            }

            setLoadingState();
        });
    }

    // Set loading state
    function setLoadingState() {
        elements.deleteBtn.disabled = true;
        elements.deleteBtn.innerHTML = `
            <i class="fas fa-spinner fa-spin"></i>
            <span>Deleting...</span>
        `;
        
        if (elements.card) {
            elements.card.classList.add('loading');
        }
    }

    // Keyboard shortcuts
    function setupKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // ESC - Cancel
            if (e.key === 'Escape' && !elements.deleteBtn.disabled) {
                e.preventDefault();
                handleCancel();
            }

            // Enter on cancel button - navigate back
            if (e.key === 'Enter' && document.activeElement === elements.cancelBtn) {
                e.preventDefault();
                handleCancel();
            }
        });
    }

    // Handle cancel with animation
    function handleCancel() {
        if (elements.card) {
            elements.card.style.animation = 'slideDown 0.25s ease-out forwards';
            setTimeout(() => {
                navigateBack();
            }, 200);
        } else {
            navigateBack();
        }
    }

    // Navigate back
    function navigateBack() {
        if (elements.cancelBtn && elements.cancelBtn.href) {
            window.location.href = elements.cancelBtn.href;
        } else {
            window.history.back();
        }
    }

    // Accessibility setup
    function setupAccessibility() {
        // Set ARIA labels
        if (!elements.deleteBtn.hasAttribute('aria-label')) {
            elements.deleteBtn.setAttribute('aria-label', 'Confirm deletion');
        }

        if (elements.cancelBtn && !elements.cancelBtn.hasAttribute('aria-label')) {
            elements.cancelBtn.setAttribute('aria-label', 'Cancel and go back');
        }

        // Focus cancel button initially
        if (elements.cancelBtn) {
            elements.cancelBtn.focus();
        }

        // Add screen reader announcement
        announceToScreenReader();
    }

    // Screen reader announcement
    function announceToScreenReader() {
        const itemName = document.querySelector('.item-name');
        if (itemName) {
            const announcement = document.createElement('div');
            announcement.setAttribute('role', 'status');
            announcement.setAttribute('aria-live', 'polite');
            announcement.className = 'visually-hidden';
            announcement.textContent = `Delete confirmation for ${itemName.textContent}. Press Escape to cancel.`;
            document.body.appendChild(announcement);
        }
    }

    // Auto-scroll to card if not visible
    function autoScroll() {
        if (!elements.card) return;

        const scrollToCard = () => {
            const rect = elements.card.getBoundingClientRect();
            const isVisible = (
                rect.top >= 0 &&
                rect.bottom <= window.innerHeight &&
                rect.left >= 0 &&
                rect.right <= window.innerWidth
            );

            if (!isVisible) {
                elements.card.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center' 
                });
            }
        };

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                setTimeout(scrollToCard, 150);
            });
        } else {
            setTimeout(scrollToCard, 150);
        }
    }

    // Prevent accidental double-click
    function preventDoubleClick() {
        elements.deleteBtn.addEventListener('dblclick', e => e.preventDefault());
    }

    // Add slide-down animation
    injectAnimation();

    function injectAnimation() {
        if (document.getElementById('delete-animations')) return;

        const style = document.createElement('style');
        style.id = 'delete-animations';
        style.textContent = `
            @keyframes slideDown {
                from {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
                to {
                    opacity: 0;
                    transform: translateY(15px) scale(0.98);
                }
            }
            .visually-hidden {
                position: absolute;
                width: 1px;
                height: 1px;
                padding: 0;
                margin: -1px;
                overflow: hidden;
                clip: rect(0, 0, 0, 0);
                white-space: nowrap;
                border: 0;
            }
        `;
        document.head.appendChild(style);
    }

})();