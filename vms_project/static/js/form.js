// static/js/form.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('mainForm');
    const submitBtn = document.getElementById('submitBtn');

    if (form && submitBtn) {
        // Form validation
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            const emptyFields = [];

            requiredFields.forEach(field => {
                const value = field.value.trim();
                if (!value) {
                    isValid = false;
                    emptyFields.push(field);
                    field.style.borderColor = '#ef4444';
                    field.classList.add('shake');
                } else {
                    field.style.borderColor = '#e5e7eb';
                    field.classList.remove('shake');
                }
            });

            if (!isValid) {
                e.preventDefault();
                
                // Focus first empty field
                if (emptyFields.length > 0) {
                    emptyFields[0].focus();
                }

                // Remove shake animation after it completes
                setTimeout(() => {
                    emptyFields.forEach(field => {
                        field.classList.remove('shake');
                    });
                }, 400);
                
                return false;
            }

            // Add loading state
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
            submitBtn.disabled = true;
            form.style.opacity = '0.6';
            form.style.pointerEvents = 'none';
        });

        // Enhanced input effects
        const formInputs = form.querySelectorAll('.modern-input, .modern-select, .modern-textarea');
        
        formInputs.forEach(input => {
            // Focus effects
            input.addEventListener('focus', function() {
                this.style.borderColor = '#6366f1';
            });

            // Blur validation
            input.addEventListener('blur', function() {
                const value = this.value.trim();
                
                if (this.hasAttribute('required') && !value) {
                    this.style.borderColor = '#ef4444';
                } else if (value) {
                    this.style.borderColor = '#10b981';
                } else {
                    this.style.borderColor = '#e5e7eb';
                }
            });

            // Input event for real-time validation
            input.addEventListener('input', function() {
                if (this.style.borderColor === 'rgb(239, 68, 68)' && this.value.trim()) {
                    this.style.borderColor = '#e5e7eb';
                }
            });
        });

        // Auto-focus on first input
        const firstInput = form.querySelector('.modern-input:not([readonly]), .modern-select');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + Enter to submit
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                submitBtn.click();
            }
        });

        // --- CUSTOM ANIMATED DROPDOWNS ---
        const initCustomSelects = () => {
            const selects = form.querySelectorAll('.modern-select:not(.custom-hidden)');
            
            selects.forEach(select => {
                const options = Array.from(select.options);
                const wrapper = document.createElement('div');
                wrapper.className = 'custom-select-wrapper';
                
                const trigger = document.createElement('div');
                trigger.className = 'custom-select-trigger';
                trigger.innerHTML = `<span>${select.options[select.selectedIndex].text}</span><i class="fas fa-chevron-down"></i>`;
                
                const optionsList = document.createElement('div');
                optionsList.className = 'custom-options';
                
                options.forEach((opt, idx) => {
                    const customOpt = document.createElement('div');
                    customOpt.className = `custom-option ${select.selectedIndex === idx ? 'selected' : ''}`;
                    customOpt.textContent = opt.text;
                    customOpt.dataset.value = opt.value;
                    
                    customOpt.addEventListener('click', () => {
                        select.selectedIndex = idx;
                        trigger.querySelector('span').textContent = opt.text;
                        optionsList.querySelectorAll('.custom-option').forEach(el => el.classList.remove('selected'));
                        customOpt.classList.add('selected');
                        wrapper.classList.remove('open');
                        
                        // Trigger native change event
                        select.dispatchEvent(new Event('change'));
                    });
                    
                    optionsList.appendChild(customOpt);
                });
                
                wrapper.appendChild(trigger);
                wrapper.appendChild(optionsList);
                
                // Hide original select but keep it for form submission
                select.classList.add('custom-hidden');
                select.style.display = 'none';
                select.parentNode.insertBefore(wrapper, select.nextSibling);
                
                trigger.addEventListener('click', (e) => {
                    e.stopPropagation();
                    // Close other selects first
                    document.querySelectorAll('.custom-select-wrapper').forEach(w => {
                        if (w !== wrapper) w.classList.remove('open');
                    });
                    wrapper.classList.toggle('open');
                });
            });
        };

        initCustomSelects();

        // Close on outside click
        window.addEventListener('click', () => {
            document.querySelectorAll('.custom-select-wrapper').forEach(w => w.classList.remove('open'));
        });
    }
});

// Character counter function
function initCharCounter(inputId, countId, counterId, maxLength) {
    const input = document.getElementById(inputId);
    const charCount = document.getElementById(countId);
    const charCounter = document.getElementById(counterId);
    
    if (!input || !charCount || !charCounter) return;

    function updateCounter() {
        const length = input.value.length;
        charCount.textContent = length;
        
        // Warning at 80% capacity
        if (length > maxLength * 0.8) {
            charCounter.classList.add('warning');
        } else {
            charCounter.classList.remove('warning');
        }
        
        // Prevent exceeding max length
        if (length > maxLength) {
            input.value = input.value.substring(0, maxLength);
            charCount.textContent = maxLength;
        }
    }

    updateCounter();
    input.addEventListener('input', updateCounter);
    input.addEventListener('paste', function() {
        setTimeout(updateCounter, 0);
    });
}