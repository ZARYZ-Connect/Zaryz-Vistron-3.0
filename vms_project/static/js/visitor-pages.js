// static/js/visitor-pages.js
// FINAL, STABLE, SAAS-SAFE VERSION

document.addEventListener('DOMContentLoaded', function () {
    initRegisterForm();
    initCameraFeatures();
    initOTPValidation();
    initApprovalForm();
    if (typeof initAnimations === "function") initAnimations();
});

// =======================================================
// REGISTER FORM (PUBLIC VISITOR REGISTER PAGE)
// =======================================================
function initRegisterForm() {
    const form = document.getElementById('visitForm');
    if (!form) return;

    // Prevent past dates
    const dateField = document.getElementById('id_visit_date');
    if (dateField) {
        const today = new Date().toISOString().split('T')[0];
        dateField.setAttribute('min', today);
    }

    const deptSelect = document.getElementById('id_department');
    const empSelect = document.getElementById('id_whom_to_meet_employee');

    if (!deptSelect || !empSelect) return;

    // ✅ SAFEST ORG CODE SOURCE (HTML > subdomain)
    const orgCode =
        form.dataset.orgCode ||
        window.location.hostname.split('.')[0];

    deptSelect.addEventListener('change', function () {
        const deptId = this.value;

        if (!deptId) {
            empSelect.innerHTML = '<option value="">Select department first</option>';
            empSelect.disabled = true;
            return;
        }

        empSelect.innerHTML = '<option value="">Loading employees...</option>';
        empSelect.disabled = true;

        // ✅ PUBLIC SAAS AJAX ENDPOINT (NO LOGIN REQUIRED)
        fetch(`/${orgCode}/ajax/employees/${deptId}/`, {
            headers: { "X-Requested-With": "XMLHttpRequest" },
            cache: "no-store",
        })
            .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })

            .then(data => {
                const employees = data.employees || [];

                empSelect.innerHTML = '<option value="">-- Select employee --</option>';

                if (employees.length > 0) {
                   employees.forEach(emp => {
                       const opt = document.createElement("option");
                       opt.value = emp.id;
                       opt.textContent = emp.name;
                       empSelect.appendChild(opt);
                   });
                   empSelect.disabled = false;
               } else {
                   empSelect.innerHTML = '<option value="">No employees found</option>';
               }
            })
            .catch(err => {
                console.error("Employee load failed:", err);
                empSelect.innerHTML = '<option value="">Error loading employees</option>';
                empSelect.disabled = true;
            });
    });

    // ✅ BLOCK SUBMIT IF PHOTO NOT CAPTURED (ADD THIS)
    form.addEventListener('submit', function (e) {
        const photoInput = document.getElementById('id_photo');

        if (!photoInput || photoInput.value.length < 100) {
            e.preventDefault();
            alert("Please capture your photo before submitting.");
            document.getElementById('openCameraBtn')
                ?.scrollIntoView({ behavior: "smooth" });
        }
    });

    // Auto focus first field
    const firstInput = form.querySelector(
        'input:not([type="hidden"]):not([readonly])'
    );
    if (firstInput) setTimeout(() => firstInput.focus(), 300);
}

// =======================================================
// CAMERA
// =======================================================
function initCameraFeatures() {
    let stream = null;

    const openBtn = document.getElementById('openCameraBtn');
    const captureBtn = document.getElementById('captureBtn');
    const video = document.getElementById('preview');
    const canvas = document.getElementById('canvas');
    const photoInput = document.getElementById('id_photo');
    const cameraWrapper = document.getElementById('cameraWrapper');
    const capturedImage = document.getElementById('capturedImage');

    if (!openBtn || !captureBtn || !video || !canvas || !photoInput) return;

    // ================= OPEN CAMERA =================
    openBtn.addEventListener('click', async () => {
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'user' }
            });

            video.srcObject = stream;
            video.muted = true;
            await video.play();

            cameraWrapper.style.display = 'block';
            openBtn.style.display = 'none';
            captureBtn.style.display = 'inline-flex';

        } catch (err) {
            alert(
                "Camera access failed.\n\n" +
                "1. HTTPS is required\n" +
                "2. Allow camera permission\n" +
                "3. Close other camera apps"
            );
        }
    });

    // ================= CAPTURE PHOTO =================
    captureBtn.addEventListener('click', () => {
        if (video.videoWidth === 0) {
            alert("Camera not ready. Please wait 1 second.");
            return;
        }

        const size = 220;
        canvas.width = size;
        canvas.height = size;

        const ctx = canvas.getContext('2d');

        ctx.save();
        ctx.beginPath();
        ctx.arc(size / 2, size / 2, size / 2, 0, Math.PI * 2);
        ctx.clip();

        ctx.translate(size, 0);
        ctx.scale(-1, 1); // mirror selfie
        ctx.drawImage(video, 0, 0, size, size);
        ctx.restore();

        const dataUrl = canvas.toDataURL('image/png');
        if (!dataUrl || dataUrl.length < 100) {
            alert("Capture failed. Try again.");
            return;
        }

        // Save photo
        photoInput.value = dataUrl;

        // Show preview
        capturedImage.src = dataUrl;
        capturedImage.style.display = 'block';
        capturedImage.style.border = '2px solid #10b981';

        // Stop camera
        if (stream) {
            stream.getTracks().forEach(t => t.stop());
            stream = null;
        }

        cameraWrapper.style.display = 'none';
        captureBtn.style.display = 'none';

        // Enable re-capture
        openBtn.innerHTML = '<i class="fas fa-redo"></i> Re-Capture Photo';
        openBtn.style.display = 'inline-flex';
    });
}

// =======================================================
// OTP
// =======================================================
function initOTPValidation() {
    const otpInput = document.querySelector('.otp-input');
    if (!otpInput) return;

    otpInput.addEventListener('input', function () {
        this.value = this.value.replace(/\D/g, '').slice(0, 6);
    });
}

// =======================================================
// APPROVAL FORM
// =======================================================
function initApprovalForm() {
    const approvalForm = document.querySelector('.approval-card-new form') || document.querySelector('#approvalForm');
    if (!approvalForm) return;

    // Support both new premium buttons and classic ones
    const acceptBtn = approvalForm.querySelector('.btn-approve-new') || approvalForm.querySelector('.btn-accept');
    const rejectBtn = approvalForm.querySelector('.btn-reject-new') || approvalForm.querySelector('.btn-reject');

    function createPremiumModal(actionType, onConfirm) {
        const isApprove = actionType === 'APPROVE';
        const modalBg = isApprove ? 'linear-gradient(135deg, #7c4dff 0%, #b388ff 100%)' : '#fee2e2';
        const modalText = isApprove ? '#fff' : '#ef4444';
        const iconClass = isApprove ? 'fa-check-circle' : 'fa-times-circle';
        const iconColor = isApprove ? '#7c4dff' : '#ef4444';
        const shadow = isApprove ? '0 4px 12px rgba(124, 77, 255, 0.3)' : 'none';

        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(8px);
            display: flex; align-items: center; justify-content: center; z-index: 99999;
            opacity: 0; transition: opacity 0.3s ease;
        `;

        overlay.innerHTML = `
            <div style="background: rgba(255, 255, 255, 0.95); padding: 32px; border-radius: 24px; max-width: 400px; width: 90%; text-align: center; box-shadow: 0 40px 80px rgba(0,0,0,0.15); border: 1px solid rgba(255,255,255,0.8); transform: translateY(20px) scale(0.95); transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);">
                <i class="fas ${iconClass}" style="font-size: 48px; color: ${iconColor}; margin-bottom: 20px;"></i>
                <h3 style="font-family: 'Inter', sans-serif; font-weight: 800; font-size: 22px; color: #1a237e; margin-bottom: 12px; letter-spacing: -0.5px;">Confirm Action</h3>
                <p style="color: #6b7280; font-size: 14px; line-height: 1.6; margin-bottom: 28px;">
                    Are you sure you want to <strong>${actionType}</strong> this visitor request?<br>This action will be finalized.
                </p>
                <div style="display: flex; gap: 12px; justify-content: center;">
                    <button class="modal-cancel-btn" style="flex: 1; padding: 12px 0; border-radius: 12px; border: 1px solid #e5e7eb; background: #f9fafb; color: #4b5563; font-weight: 600; font-size: 14px; cursor: pointer; transition: all 0.2s;">Cancel</button>
                    <button class="modal-confirm-btn" style="flex: 1; padding: 12px 0; border-radius: 12px; border: none; background: ${modalBg}; color: ${modalText}; font-weight: 700; font-size: 14px; cursor: pointer; transition: all 0.2s; box-shadow: ${shadow};">Yes, ${actionType}</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        // Animate Intro
        requestAnimationFrame(() => {
            overlay.style.opacity = '1';
            overlay.firstElementChild.style.transform = 'translateY(0) scale(1)';
        });

        // Hover effects for buttons
        const btnCancel = overlay.querySelector('.modal-cancel-btn');
        const btnConfirm = overlay.querySelector('.modal-confirm-btn');
        
        btnCancel.onmouseover = () => btnCancel.style.background = '#f3f4f6';
        btnCancel.onmouseout = () => btnCancel.style.background = '#f9fafb';
        
        if (isApprove) {
            btnConfirm.onmouseover = () => { btnConfirm.style.transform = 'translateY(-2px)'; btnConfirm.style.boxShadow = '0 6px 16px rgba(124, 77, 255, 0.4)'; };
            btnConfirm.onmouseout = () => { btnConfirm.style.transform = 'translateY(0)'; btnConfirm.style.boxShadow = shadow; };
        } else {
            btnConfirm.onmouseover = () => btnConfirm.style.background = '#fecaca';
            btnConfirm.onmouseout = () => btnConfirm.style.background = modalBg;
        }

        // Close logic
        const close = () => {
            overlay.style.opacity = '0';
            overlay.firstElementChild.style.transform = 'translateY(20px) scale(0.95)';
            setTimeout(() => overlay.remove(), 300);
        };

        btnCancel.addEventListener('click', close);
        btnConfirm.addEventListener('click', () => {
            onConfirm();
            close();
        });
    }

    if (acceptBtn) {
        acceptBtn.addEventListener('click', function (e) {
            e.preventDefault();
            const decisionField = document.getElementById('decisionField');
            if (decisionField) decisionField.value = 'accept';
            createPremiumModal('APPROVE', () => approvalForm.submit());
        });
    }

    if (rejectBtn) {
        rejectBtn.addEventListener('click', function (e) {
            e.preventDefault();
            const decisionField = document.getElementById('decisionField');
            if (decisionField) decisionField.value = 'reject';
            createPremiumModal('REJECT', () => approvalForm.submit());
        });
    }
}

// =======================================================
// UTILITIES
// =======================================================
function smoothScrollTo(element) {
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        background: ${type === 'success'
            ? '#10b981'
            : type === 'error'
            ? '#ef4444'
            : '#6366f1'};
        color: white;
        border-radius: 12px;
        z-index: 10000;
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

// Keyboard shortcut
document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const activeForm = document.querySelector('form:focus-within');
        if (activeForm) {
            e.preventDefault();
            activeForm.querySelector('button[type="submit"]')?.click();
        }
    }
});
