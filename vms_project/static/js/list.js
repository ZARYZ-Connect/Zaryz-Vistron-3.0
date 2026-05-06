// static/js/list.js
document.addEventListener('DOMContentLoaded', function() {
    // 1. Table Row Effects Removed
    /* tableRows logic removed */

    // 2. Custom Select Unified Logic
    const wrappers = document.querySelectorAll('.custom-select-wrapper');
    wrappers.forEach(wrapper => {
      const select = wrapper.querySelector('select');
      const trigger = wrapper.querySelector('[class*="custom-select-trigger"]');
      const triggerSpan = trigger ? trigger.querySelector('span') : null;
      const options = wrapper.querySelectorAll('.custom-option');
      
      if (!select || !trigger || !triggerSpan) return;

      const selectedOption = select.options[select.selectedIndex];
      if (selectedOption) {
        triggerSpan.textContent = selectedOption.textContent;
        options.forEach(opt => {
          if (opt.dataset.value === select.value) opt.classList.add('selected');
        });
      }

      wrapper.addEventListener('click', function(e) {
        e.stopPropagation();
        wrappers.forEach(w => { if(w !== wrapper) w.classList.remove('open'); });
        this.classList.toggle('open');
      });

      options.forEach(option => {
        option.addEventListener('click', function() {
          const val = this.dataset.value;
          select.value = val;
          triggerSpan.textContent = this.textContent;
          options.forEach(o => o.classList.remove('selected'));
          this.classList.add('selected');
          wrapper.classList.remove('open');
          
          if (document.querySelector('.list-card')) {
            document.querySelector('.list-card').style.opacity = '0.6';
          }
          
          // Custom Logic Dispatch
          if (select.classList.contains('per-page-select')) {
            const urlParams = new URLSearchParams(window.location.search);
            urlParams.set('per_page', val);
            urlParams.set('page', 1);
            window.location.search = urlParams.toString();
          } else {
            const form = select.closest('form');
            if (form) form.submit();
          }
        });
      });
    });

    const pageExpander = document.getElementById('pageExpander');
    if (pageExpander) {
        pageExpander.addEventListener('click', function(e) {
            e.stopPropagation();
            this.classList.toggle('expanded');
        });
        
        const pillOptions = pageExpander.querySelectorAll('.pill-option');
        pillOptions.forEach(opt => {
            opt.addEventListener('click', function(e) {
                e.stopPropagation();
                navigatePerPage(this.dataset.value);
            });
        });
    }

    function navigatePerPage(val) {
        const urlParams = new URLSearchParams(window.location.search);
        urlParams.set('per_page', val);
        urlParams.set('page', 1);
        if (document.querySelector('.list-card')) document.querySelector('.list-card').style.opacity = '0.6';
        window.location.search = urlParams.toString();
    }

    document.addEventListener('click', () => {
      wrappers.forEach(w => w.classList.remove('open'));
      if (pageExpander) pageExpander.classList.remove('expanded');
    });

    // 3. Staggered animation
    const tableRowsAnimated = document.querySelectorAll('.stagger-animation tr');
    tableRowsAnimated.forEach((row, index) => {
        row.style.animationDelay = `${(index + 1) * 0.1}s`;
    });

    // 4. File input
    const fileInput = document.getElementById("fileInput");
    if (fileInput) {
        fileInput.addEventListener("change", function() {
            const fileName = document.getElementById("fileName");
            fileName.textContent = this.files[0]?.name || "No file selected";
        });
    }
    // 5. Magnetic Hover Effect for "Details" Buttons
    const magneticBtns = document.querySelectorAll('.btn-view-modern, .btn-view-ticket');
    magneticBtns.forEach(btn => {
        btn.addEventListener('mousemove', function(e) {
            const position = btn.getBoundingClientRect();
            const x = e.pageX - position.left - position.width / 2;
            const y = e.pageY - position.top - position.height / 2;
            
            btn.style.transform = `translate(${x * 0.3}px, ${y * 0.3}px) scale(1.05)`;
            if (btn.querySelector('i')) {
                btn.querySelector('i').style.transform = `translate(${x * 0.1}px, ${y * 0.1}px)`;
            }
        });

        btn.addEventListener('mouseleave', function() {
            btn.style.transform = '';
            if (btn.querySelector('i')) {
                btn.querySelector('i').style.transform = '';
            }
        });
    });
});
