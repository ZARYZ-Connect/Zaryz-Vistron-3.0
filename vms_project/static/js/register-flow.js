document.addEventListener("DOMContentLoaded", () => {

  /* =========================================
     STEP FLOW LOGIC WITH VALIDATION
  ========================================= */

  const steps = document.querySelectorAll(".flow-step");
  const indicators = document.querySelectorAll(".stepper .step");
  let current = 0;

  function showStep(index) {
    steps.forEach((step, i) => {
      step.classList.toggle("active", i === index);
    });

    indicators.forEach((step, i) => {
      step.classList.remove("active", "done");
      if (i < index) step.classList.add("done");
      if (i === index) step.classList.add("active");
    });

    // Smooth scroll to top on step change
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function showToast(message) {
    const toast = document.getElementById("vms-toast");
    if (toast) {
      toast.innerText = message;
      toast.className = "show";
      setTimeout(() => { toast.className = toast.className.replace("show", ""); }, 3000);
    }
  }

  function setError(input, message) {
    const group = input.closest(".form-group") || input.parentElement;
    group.classList.add("has-error");
    const errorDiv = group.querySelector(".field-error");
    if (errorDiv) {
      errorDiv.innerText = message;
      errorDiv.style.display = "block";
    }
  }

  function clearError(input) {
    const group = input.closest(".form-group") || input.parentElement;
    group.classList.remove("has-error");
    const errorDiv = group.querySelector(".field-error");
    if (errorDiv && !errorDiv.classList.contains("server-error")) {
      errorDiv.style.display = "none";
    }
  }

  showStep(current);

  document.querySelectorAll(".next").forEach(btn => {
    btn.addEventListener("click", () => {

      const step = steps[current];
      const inputs = step.querySelectorAll("input, select, textarea");

      let valid = true;

      inputs.forEach(input => {

        if (input.type === "hidden") return;

        const value = input.value ? input.value.trim() : "";

        // Required check
        if (value === "") {
          input.classList.add("input-error");
          valid = false;
          if (input.name === "visit_type") {
            const dropdownTrigger = document.querySelector(".vms-dropdown-trigger");
            if (dropdownTrigger) dropdownTrigger.classList.add("input-error");
          }
        } else {
          input.classList.remove("input-error");
          if (input.name === "visit_type") {
            const dropdownTrigger = document.querySelector(".vms-dropdown-trigger");
            if (dropdownTrigger) dropdownTrigger.classList.remove("input-error");
          }
        }

        // Phone validation
        if (input.classList.contains("phone-input") || input.name === "phone") {
          if (!/^[0-9]{10}$/.test(value)) {
            setError(input, "Phone number must be exactly 10 digits");
            valid = false;
          } else {
            clearError(input);
          }
        }

        // ✅ Email validation
        if (input.type === "email" || input.name === "email") {
          const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

          if (!emailPattern.test(value)) {
            setError(input, "Please enter a valid email address");
            valid = false;
          } else {
            clearError(input);
          }
        }

      });

      // 🚨 STOP IF INVALID
      /* ===============================
         EXTRA VALIDATIONS
      =============================== */

      // Name validation
      const nameInput = step.querySelector("input[name='full_name']");
      if (nameInput) {

        const nameVal = nameInput.value.trim();
        const namePattern = /^[A-Za-z\s]{3,}$/;

        if (!namePattern.test(nameVal)) {
          nameInput.classList.add("input-error");
          valid = false;
        }

      }

      // Email validation
      const emailInput = step.querySelector("input[name='email']");
      if (emailInput) {

        const emailVal = emailInput.value.trim();
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailPattern.test(emailVal)) {
          emailInput.classList.add("input-error");
          valid = false;
        }

      }

      // Date validation
      const visitDateInput = step.querySelector("input[name='visit_date']");
      if (visitDateInput) {

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const selectedDate = new Date(visitDateInput.value);

        if (selectedDate < today) {
          visitDateInput.classList.add("input-error");
          valid = false;
        }

      }

      // Time validation
      const startTime = step.querySelector("input[name='start_time']");
      const endTime = step.querySelector("input[name='end_time']");

      if (startTime && endTime) {

        if (startTime.value && endTime.value) {

          if (startTime.value >= endTime.value) {

            startTime.classList.add("input-error");
            endTime.classList.add("input-error");

            valid = false;

          }

        }

      }

      if (!valid) return;

      // Move forward
      if (current < steps.length - 1) {
        current++;
        showStep(current);
      }

    });
  });

  document.querySelectorAll(".back").forEach(btn => {
    btn.addEventListener("click", () => {
      if (current > 0) {
        current--;
        showStep(current);
      }
    });
  });



  /* =========================================
     ANIMATED DATE PICKER
  ========================================= */

  class VMSDatePicker {
    constructor(inputName) {
      this.input = document.querySelector(`input[name='${inputName}']`);
      if (!this.input) return;

      this.init();
    }

    init() {
      // Use focus and click to trigger
      this.input.addEventListener("focus", (e) => {
        this.open();
      });

      this.input.addEventListener("click", (e) => {
        this.open();
      });

      // Prevent native keyboard on mobile if possible
      this.input.setAttribute("readonly", true);
      this.input.style.cursor = "pointer";
    }

    open() {
      if (document.querySelector(".vms-custom-picker")) return;

      // Close other pickers
      document.querySelectorAll('.vms-time-picker, .vms-custom-picker').forEach(p => {
        p.classList.add('closing');
        setTimeout(() => p.remove(), 300);
      });

      const picker = document.createElement("div");
      picker.className = "vms-custom-picker picker-animated";

      picker.style.position = "fixed";
      picker.style.top = "50%";
      picker.style.left = "50%";
      picker.style.width = `260px`;
      picker.style.minWidth = "260px";

      // Match the app's font
      picker.style.fontFamily = "Inter, sans-serif";
      picker.style.fontSize = "0.85rem";

      const now = new Date();
      this.render(picker, now.getFullYear(), now.getMonth());

      document.body.appendChild(picker);

      const closeHandler = (e) => {
        if (!picker.contains(e.target) && e.target !== this.input) {
          picker.classList.add("closing");
          setTimeout(() => picker.remove(), 300);
          document.removeEventListener("mousedown", closeHandler);
        }
      };
      this.closeHandler = closeHandler;
      setTimeout(() => document.addEventListener("mousedown", closeHandler), 10);
    }

    render(container, year, month) {
      const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
      const firstDay = new Date(year, month, 1).getDay();
      const daysInMonth = new Date(year, month + 1, 0).getDate();

      const todayDate = new Date();
      todayDate.setHours(0, 0, 0, 0);

      const currentYear = todayDate.getFullYear();
      const currentMonth = todayDate.getMonth();
      const disablePrevMonth = year < currentYear || (year === currentYear && month <= currentMonth);

      let html = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; user-select:none;">
          <button type="button" class="prev-m" style="background:rgba(255,255,255,0.1); border:none; color:#fff; cursor:pointer; width:26px; height:26px; border-radius:50%; display:flex; align-items:center; justify-content:center; ${disablePrevMonth ? 'opacity:0.3; pointer-events:none;' : ''}">&lt;</button>
          <span style="font-weight:600; color:#fff; font-size:14px;">${monthNames[month]} ${year}</span>
          <button type="button" class="next-m" style="background:rgba(255,255,255,0.1); border:none; color:#fff; cursor:pointer; width:26px; height:26px; border-radius:50%; display:flex; align-items:center; justify-content:center;">&gt;</button>
        </div>
        <div style="display:grid; grid-template-columns:repeat(7, 1fr); gap:4px; text-align:center; user-select:none;">
          ${["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"].map(d => `<div style="font-size:0.7rem; opacity:0.5; color:#fff; padding-bottom:4px;">${d}</div>`).join("")}
      `;

      for (let i = 0; i < firstDay; i++) html += "<div></div>";
      
      let selectedDateStr = this.input.value; // e.g. "2026-03-27"

      for (let d = 1; d <= daysInMonth; d++) {
        const iterDate = new Date(year, month, d);
        const isPast = iterDate < todayDate;

        const isToday = todayDate.getDate() === d && todayDate.getMonth() === month && todayDate.getFullYear() === year;
        const currentVal = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
        const isSelected = selectedDateStr === currentVal;
        
        let extraClass = isSelected ? "selected-day" : "";
        if (isPast) extraClass += " disabled-day";

        let opacityStyle = isPast ? 'opacity:0.3; cursor:not-allowed;' : 'cursor:pointer;';
        let pointerEvents = isPast ? 'pointer-events:none;' : '';
        let borderStyle = isToday ? 'border:1px solid #6366f1;' : 'border:1px solid transparent;';
        
        html += `<div class="day-opt ${extraClass}" style="padding:6px; border-radius:8px; transition:0.2s; color:#fff; font-size:13px; ${opacityStyle} ${pointerEvents} ${borderStyle}" data-day="${d}">${d}</div>`;
      }
      html += "</div>";

      container.innerHTML = html;

      container.querySelector(".prev-m").onclick = (e) => { e.stopPropagation(); this.render(container, month === 0 ? year - 1 : year, month === 0 ? 11 : month - 1); };
      container.querySelector(".next-m").onclick = (e) => { e.stopPropagation(); this.render(container, month === 11 ? year + 1 : year, month === 11 ? 0 : month + 1); };

      container.querySelectorAll(".day-opt").forEach(opt => {
        opt.onclick = () => {
          const val = `${year}-${String(month + 1).padStart(2, '0')}-${String(opt.dataset.day).padStart(2, '0')}`;
          this.input.value = val;
          this.input.dispatchEvent(new Event('input')); // Trigger any input listeners
          
          container.querySelectorAll(".day-opt").forEach(o => o.classList.remove('selected-day'));
          opt.classList.add('selected-day');

          container.classList.add("closing");
          setTimeout(() => container.remove(), 250);
          if (this.closeHandler) {
            document.removeEventListener("mousedown", this.closeHandler);
          }
        };
      });
    }
  }

  new VMSDatePicker("visit_date");

  /* =========================================
     ANIMATED TIME PICKER
  ========================================= */

  class VMSTimePicker {
    constructor(inputName) {
      this.input = document.querySelector(`input[name='${inputName}']`);
      if (!this.input) return;

      this.init();
    }

    init() {
      // Use focus and click to trigger
      this.input.addEventListener("focus", (e) => {
        this.open();
      });

      this.input.addEventListener("click", (e) => {
        this.open();
      });

      // Prevent native keyboard on mobile if possible
      this.input.setAttribute("readonly", true);
      this.input.style.cursor = "pointer";
    }

    open() {
      if (document.querySelector(`.vms-time-picker[data-for="${this.input.name}"]`)) return;

      // Close other pickers
      document.querySelectorAll('.vms-time-picker, .vms-custom-picker').forEach(p => {
        p.classList.add('closing');
        setTimeout(() => p.remove(), 300);
      });

      const picker = document.createElement("div");
      picker.className = "vms-time-picker picker-animated list-picker-time";
      picker.dataset.for = this.input.name;

      picker.style.position = "fixed";
      picker.style.top = "50%";
      picker.style.left = "50%";
      picker.style.width = `280px`;
      picker.style.minWidth = "280px";

      picker.style.fontFamily = "Inter, sans-serif";
      picker.style.fontSize = "0.95rem";

      // Parse current value or use default
      let h = "12", m = "00", ampm = "PM";
      if (this.input.value) {
         let parts = this.input.value.split(":");
         if(parts.length >= 2) {
             let hours24 = parseInt(parts[0], 10);
             let mins = parseInt(parts[1], 10);
             ampm = hours24 >= 12 ? "PM" : "AM";
             let hours12 = hours24 % 12 || 12;
             h = String(hours12).padStart(2, '0');
             m = String(mins).padStart(2, '0');
         }
      } else {
         const now = new Date();
         let hours24 = now.getHours();
         let mins = now.getMinutes();
         ampm = hours24 >= 12 ? "PM" : "AM";
         let hours12 = hours24 % 12 || 12;
         h = String(hours12).padStart(2, '0');
         m = String(mins).padStart(2, '0');
      }
      
      this.selectedHour = h;
      this.selectedMinute = m;
      this.selectedAmpm = ampm;

      this.render(picker);

      document.body.appendChild(picker);

      const closeHandler = (e) => {
        if (!picker.contains(e.target) && e.target !== this.input) {
          this.close(picker);
          document.removeEventListener("mousedown", closeHandler);
        }
      };
      
      this.closeHandler = closeHandler;
      setTimeout(() => document.addEventListener("mousedown", closeHandler), 10);
    }
    
    close(picker) {
      picker.classList.add("closing");
      setTimeout(() => picker.remove(), 300);
    }

    render(container) {
      let hoursHtml = "";
      for(let i=1; i<=12; i++) {
        let val = String(i).padStart(2, '0');
        let sel = (val === this.selectedHour) ? 'selected-opt' : '';
        hoursHtml += `<div class="sc-opt hour-opt ${sel}" data-val="${val}">${val}</div>`;
      }

      let minsHtml = "";
      for(let i=0; i<=59; i++) {
        let val = String(i).padStart(2, '0');
        let sel = (val === this.selectedMinute) ? 'selected-opt' : '';
        minsHtml += `<div class="sc-opt min-opt ${sel}" data-val="${val}">${val}</div>`;
      }

      let topPart = `
        <div style="text-align:center; font-weight:600; margin-bottom:12px; color:#fff;">Select Time</div>
        <div style="display:flex; justify-content:space-between; align-items:flex-start; height: 180px; gap: 8px;">
          <div class="time-options scroll-col" style="flex:1; overflow-y:auto; height:100%; border-radius:8px; background:rgba(0,0,0,0.2); padding:4px;">
             ${hoursHtml}
          </div>
          <div style="display:flex; align-items:center; padding-top:80px; font-weight:bold; color:rgba(255,255,255,0.5);">:</div>
          <div class="time-options scroll-col" style="flex:1; overflow-y:auto; height:100%; border-radius:8px; background:rgba(0,0,0,0.2); padding:4px;">
             ${minsHtml}
          </div>
          <div class="time-options scroll-col" style="width:60px; overflow-y:auto; height:100%; border-radius:8px; background:rgba(0,0,0,0.2); padding:4px;">
             <div class="sc-opt ampm-opt ${(this.selectedAmpm==='AM')?'selected-opt':''}" data-val="AM">AM</div>
             <div class="sc-opt ampm-opt ${(this.selectedAmpm==='PM')?'selected-opt':''}" data-val="PM">PM</div>
          </div>
        </div>
        <div style="display:flex; justify-content:space-between; margin-top:16px;">
          <button type="button" class="btn ghost t-cancel" style="padding:10px 20px; font-size:13px;">Cancel</button>
          <button type="button" class="btn primary t-confirm" style="padding:10px 20px; font-size:13px;">Set Time</button>
        </div>
      `;

      container.innerHTML = topPart;

      const pickOption = (nodes, varName) => {
         nodes.forEach(opt => {
             opt.onclick = () => {
                 nodes.forEach(o => o.classList.remove("selected-opt"));
                 opt.classList.add("selected-opt");
                 this[varName] = opt.dataset.val;
             };
         });
      };

      pickOption(container.querySelectorAll('.hour-opt'), 'selectedHour');
      pickOption(container.querySelectorAll('.min-opt'), 'selectedMinute');
      pickOption(container.querySelectorAll('.ampm-opt'), 'selectedAmpm');

      // auto scroll to selected
      setTimeout(() => {
          ['hour-opt', 'min-opt', 'ampm-opt'].forEach(cls => {
             const active = container.querySelector(`.${cls}.selected-opt`);
             if (active) active.scrollIntoView({ block: "center", behavior: "auto" });
          });
      }, 10);

      container.querySelector('.t-cancel').onclick = () => {
          this.close(container);
          if (this.closeHandler) document.removeEventListener("mousedown", this.closeHandler);
      };

      container.querySelector('.t-confirm').onclick = () => {
          let h24 = parseInt(this.selectedHour, 10);
          if (this.selectedAmpm === "PM" && h24 < 12) h24 += 12;
          if (this.selectedAmpm === "AM" && h24 === 12) h24 = 0;
          let val = `${String(h24).padStart(2,'0')}:${this.selectedMinute}`;
          this.input.value = val;
          this.input.dispatchEvent(new Event('input'));

          this.close(container);
          if (this.closeHandler) document.removeEventListener("mousedown", this.closeHandler);
      };
    }
  }

  new VMSTimePicker("start_time");
  new VMSTimePicker("end_time");


  /* =========================================
     DEPARTMENT → EMPLOYEE AJAX FILTER
  ========================================= */

  const departmentSelect = document.querySelector("select[name='department']");
  const employeeSelect = document.querySelector("select[name='whom_to_meet_employee']");

  if (departmentSelect && employeeSelect) {

    // Disable employee dropdown initially
    employeeSelect.disabled = true;
    employeeSelect.innerHTML = "<option value=''>Select department first</option>";

    departmentSelect.addEventListener("change", function () {

      const deptId = this.value;

      // If no department selected
      if (!deptId) {

        employeeSelect.disabled = true;
        employeeSelect.innerHTML = "<option value=''>Select department first</option>";

        return;
      }

      // Enable dropdown
      employeeSelect.disabled = false;
      employeeSelect.innerHTML = "<option value=''>Loading...</option>";

      fetch(`${window.location.origin}/dashboard/ajax/public/employees/${deptId}/`)
        .then(response => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          return response.json();
        })
        .then(data => {

          employeeSelect.innerHTML = "<option value=''>-- Select Person --</option>";

          if (!data.employees || data.employees.length === 0) {

            employeeSelect.innerHTML = "<option value=''>No employees found</option>";
            return;

          }

          data.employees.forEach(emp => {

            const option = document.createElement("option");

            option.value = emp.id;
            option.textContent = emp.name;

            employeeSelect.appendChild(option);

          });

        })
        .catch(error => {

          console.error("Employee loading error:", error);

          employeeSelect.innerHTML = "<option value=''>Error loading employees</option>";

        });

    });

  }

  /* =========================================
     CAMERA LOGIC
  ========================================= */

  const openCameraBtn = document.getElementById("openCamera");
  const video = document.getElementById("video");
  const canvas = document.getElementById("canvas");
  const photoPreview = document.getElementById("photoPreview");
  const submitBtn = document.getElementById("submitBtn");
  const hiddenPhotoInput = document.querySelector("input[name='photo']");

  let stream = null;
  let cameraOpen = false;

  if (!openCameraBtn) return;

  openCameraBtn.addEventListener("click", async () => {

    if (!cameraOpen) {

      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });

        video.srcObject = stream;
        video.style.display = "block";

        photoPreview.innerHTML = "";
        photoPreview.appendChild(video);

        openCameraBtn.innerText = "📷 Take Photo";
        cameraOpen = true;

      } catch (error) {
        alert("Camera access denied or not available.");
        console.error(error);
      }

    } else {

      if (!video.videoWidth) return;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      const ctx = canvas.getContext("2d");
      ctx.drawImage(video, 0, 0);

      const imageData = canvas.toDataURL("image/png");

      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }

      video.style.display = "none";
      cameraOpen = false;

      photoPreview.innerHTML = `
        <img src="${imageData}"
             style="width:100%;height:100%;object-fit:cover;border-radius:50%;">
      `;

      if (hiddenPhotoInput) {
        hiddenPhotoInput.value = imageData;
      }

      if (submitBtn) {
        submitBtn.disabled = false;
      }

      openCameraBtn.innerText = "📸 Retake Photo";
    }

  });


  /* =========================================
     FINAL SUBMIT VALIDATION (PHOTO REQUIRED)
  ========================================= */

  const form = document.querySelector("form");

  if (form) {
    form.addEventListener("submit", function (e) {
      if (!hiddenPhotoInput.value) {
        showToast("Please capture your photo before completing registration.");
        e.preventDefault();
      }

    });
  }
  /* ===================================
     REUSABLE VMS DROPDOWN GENERATOR
  =================================== */
  function initVMSDropdown(name, isVisitType = false) {
    const originalSelect = document.querySelector(`select[name="${name}"]`);
    if (!originalSelect) return;

    // Prevent double initialization
    if (originalSelect.dataset.vmsInit) return;
    originalSelect.dataset.vmsInit = "true";

    // Hide native select
    originalSelect.style.display = "none";

    // Wrapper
    const dropdownContainer = document.createElement("div");
    dropdownContainer.className = "vms-dropdown";
    originalSelect.parentNode.insertBefore(dropdownContainer, originalSelect);
    dropdownContainer.appendChild(originalSelect);

    // Trigger
    const trigger = document.createElement("div");
    trigger.className = "vms-dropdown-trigger animated-field";
    trigger.tabIndex = 0;
    trigger.innerHTML = `<span class="vms-dropdown-text"></span>`;
    dropdownContainer.appendChild(trigger);

    // Menu
    const menu = document.createElement("div");
    menu.className = "vms-dropdown-menu";
    dropdownContainer.appendChild(menu);

    function rebuildItems() {
      // Clear current menu
      menu.innerHTML = "";
      
      const selectedOpt = originalSelect.options[originalSelect.selectedIndex];
      const initialText = selectedOpt ? selectedOpt.text : "Select...";
      const dropdownText = trigger.querySelector(".vms-dropdown-text");
      
      dropdownText.innerHTML = initialText;
      dropdownText.style.opacity = (selectedOpt && !selectedOpt.value) ? "0.7" : "1";

      const options = Array.from(originalSelect.options);
      options.forEach((opt) => {
        // Skip the empty/placeholder option — don't render it as a list item
        if (!opt.value) return;

        const item = document.createElement("div");
        item.className = "vms-dropdown-item";
        if (opt.selected) item.classList.add("selected");

        const textHTML = opt.text;

        item.innerHTML = `<span>${textHTML}</span>`;

        item.addEventListener("click", (e) => {
          e.stopPropagation();
          
          // 1. Cross-fade the text
          dropdownText.style.opacity = "0";
          setTimeout(() => {
            dropdownText.innerHTML = textHTML;
            dropdownText.style.opacity = !opt.value ? "0.7" : "1";
          }, 150);

          // 2. Pulse background highlight
          trigger.style.background = "rgba(139, 92, 246, 0.3)";
          setTimeout(() => { trigger.style.background = ""; }, 300);

          originalSelect.value = opt.value;
          originalSelect.dispatchEvent(new Event("change"));

          trigger.classList.remove("input-error");
          dropdownContainer.classList.remove("open");

          Array.from(menu.children).forEach(child => child.classList.remove("selected"));
          item.classList.add("selected");
        });

        menu.appendChild(item);
      });
    }

    // Initial build
    rebuildItems();

    // Watch for dynamic updates (AJAX filters)
    const observer = new MutationObserver(() => rebuildItems());
    observer.observe(originalSelect, { childList: true });

    // Interactivity
    trigger.addEventListener("click", () => {
      dropdownContainer.classList.toggle("open");
    });

    document.addEventListener("click", (e) => {
      if (!dropdownContainer.contains(e.target)) {
        dropdownContainer.classList.remove("open");
      }
    });
  }

  // Initialize for all three
  initVMSDropdown("visit_type", true);
  initVMSDropdown("department", false);
  initVMSDropdown("whom_to_meet_employee", false);
  /* =========================================
     REAL-TIME VALIDATION
  ========================================= */
  const phoneField = document.querySelector("input[name='phone']");
  if (phoneField) {
    phoneField.addEventListener("input", function (e) {
      // Force only digits
      this.value = this.value.replace(/\D/g, "");

      // Restrict to 10 digits
      if (this.value.length > 10) {
        this.value = this.value.slice(0, 10);
      }

      // Real-time error clearing if it becomes valid
      if (this.value.length === 10) {
        clearError(this);
      }
    });

    // Prevent non-numeric key presses
    phoneField.addEventListener("keydown", function (e) {
      const allowedKeys = ["Backspace", "ArrowLeft", "ArrowRight", "Tab", "Delete", "Enter"];
      if (!/[0-9]/.test(e.key) && !allowedKeys.includes(e.key)) {
        e.preventDefault();
      }
    });
  }

  const emailField = document.querySelector("input[name='email']");
  if (emailField) {
    emailField.addEventListener("input", function () {
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (this.value.trim() === "" || emailPattern.test(this.value.trim())) {
        clearError(this);
      }
    });
  }



}); // ← THIS closes DOMContentLoaded
