// static/js/qr-scanner.js

/* CSRF cookie helper */
function getCookie(name) {
    const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? m.pop() : '';
}

const csrftoken = getCookie('csrftoken');
let qrScanner = null;
let isScanning = false;

// DOM Elements
const statusEl = document.getElementById('scan-status');
const resultCard = document.getElementById('scan-result');
const msgEl = document.getElementById('scan-message');
const subEl = document.getElementById('scan-sub');
const retryBtn = document.getElementById('retry-scan');
const openDetailBtn = document.getElementById('open-detail');
const resultIcon = document.getElementById('result-icon');

// Status Management
function setStatus(text, type = 'scanning') {
    statusEl.innerText = text;
    statusEl.className = `scan-status ${type}`;
}

// Result Display
function showResult(message, scheduled = '', allowed = false, redirect = null) {
    resultCard.style.display = 'block';

    msgEl.innerText = message || '';

    if (scheduled) {
        subEl.innerHTML = `
            <div style="margin-top:15px;font-size:14px;opacity:0.8;">
                <strong>Scheduled Time</strong><br>
                ${scheduled}
            </div>
        `;
    } else {
        subEl.innerHTML = '';
    }

    if (allowed) {
        msgEl.className = 'scan-message success';
        resultIcon.className = 'result-icon success';
        resultIcon.innerHTML = '<i class="fas fa-check-circle"></i>';
        openDetailBtn.style.display = 'inline-flex';
        openDetailBtn.dataset.redirect = redirect || '';
    } else {
        msgEl.className = 'scan-message error';
        resultIcon.className = 'result-icon error';
        resultIcon.innerHTML = '<i class="fas fa-times-circle"></i>';
        openDetailBtn.style.display = 'none';
    }

    resultCard.style.animation = 'slideUp 0.4s ease-out';
}

function hideResult() {
    resultCard.style.display = 'none';
    msgEl.innerText = '';
    subEl.innerText = '';
}

// Script Loader
function loadScript(url) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = url;
        script.async = true;
        script.onload = () => resolve();
        script.onerror = () => reject(new Error(`Failed to load ${url}`));
        document.head.appendChild(script);
    });
}

// Camera Permission Pre-check
async function requestCameraPermission() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            stream.getTracks().forEach(track => track.stop());
            return true;
        } catch (error) {
            console.warn('Camera permission denied:', error);
            return false;
        }
    }
    return false;
}

// Initialize QR Scanner
(async function init() {
    // Pre-check camera permission
    setStatus('Checking camera access...', 'scanning');
    await requestCameraPermission();
    
    // Load QR library
    const cdnUrl = "https://unpkg.com/html5-qrcode@2.3.7/minified/html5-qrcode.min.js";
    const localUrl = document.getElementById('local-qr-lib-url')?.value || '';
    
    try {
        setStatus('Loading QR scanner...', 'scanning');
        await loadScript(cdnUrl);
        setStatus('Scanner ready', 'success');
        setTimeout(() => startScanner(), 500);
    } catch (error) {
        console.warn('CDN failed, trying local:', error);
        if (localUrl) {
            try {
                await loadScript(localUrl);
                setStatus('Scanner ready (local)', 'success');
                setTimeout(() => startScanner(), 500);
            } catch (localError) {
                console.error('Local library load failed:', localError);
                setStatus('Failed to load QR scanner library', 'error');
            }
        } else {
            setStatus('QR library not available', 'error');
        }
    }
})();

// Start QR Scanner
async function startScanner() {
    hideResult();
    setStatus('Initializing camera...', 'scanning');
    
    // Stop existing scanner
    if (qrScanner) {
        try {
            await qrScanner.stop();
        } catch (e) {
            console.warn('Error stopping previous scanner:', e);
        }
        qrScanner = null;
    }
    
    if (typeof Html5Qrcode === 'undefined') {
        setStatus('QR scanner not available', 'error');
        return;
    }
    
    qrScanner = new Html5Qrcode("reader");
    isScanning = false;
    
    try {
        const devices = await Html5Qrcode.getCameras();
        
        if (!devices || devices.length === 0) {
            setStatus('No camera found on this device', 'error');
            return;
        }
        
        // Prefer back camera on mobile
        const backCamera = devices.find(d => d.label.toLowerCase().includes('back')) || devices[0];
        const cameraId = backCamera.id;
        
        await qrScanner.start(
            cameraId,
            {
                fps: 10,
                qrbox: { width: 250, height: 250 },
                aspectRatio: 1.0
            },
            async (decodedText) => {
                if (isScanning) return; // Prevent duplicate scans
                isScanning = true;
                
                console.log('QR Code detected:', decodedText);
                setStatus('QR code detected, verifying...', 'scanning');
                
                // Stop camera
                try {
                    await qrScanner.stop();
                } catch (err) {
                    console.warn('Stop error:', err);
                }
                
                // Verify with server
                await verifyQRCode(decodedText);
            },
            (errorMessage) => {
                // Scanning errors (ignore - these fire constantly)
            }
        );
        
        setStatus('Camera active - Show QR code to camera', 'success');
        
    } catch (error) {
        console.error('Camera start error:', error);
        setStatus(`Unable to start camera: ${error.message || error}`, 'error');
    }
}

// Verify QR Code with Server
async function verifyQRCode(uuid) {
    setStatus('Verifying visitor...', 'scanning');
    
    try {
        const verifyUrl = document.getElementById('verify-qr-url')?.value || '/security/verify-qr/';
        
        const response = await fetch(verifyUrl, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ uuid: uuid })
        });
        
        const data = await response.json();
        console.log('Verification response:', data);
        
        if (data && data.ok) {
            const scheduledTime = data.scheduled || '';
            const message = data.message || (data.allowed ? 'Visit Valid ✓' : 'Access Denied');
            
            showResult(
                message,
                scheduledTime,
                !!data.allowed,
                data.redirect || null
            );
            
            setStatus(
                data.allowed ? 'Access Granted' : 'Access Denied',
                data.allowed ? 'success' : 'error'
            );
            
            // Play sound feedback (optional)
            if (data.allowed) {
                playSuccessSound();
            } else {
                playErrorSound();
            }
            
        } else {
            const errorMsg = (data && (data.message || data.error)) || 'Visitor not found';
            showResult(errorMsg, '', false, null);
            setStatus('Verification Failed', 'error');
            playErrorSound();
        }
        
        isScanning = false;
        
    } catch (error) {
        console.error('Verification error:', error);
        showResult('Network or server error occurred', 'Please check connection and try again', false, null);
        setStatus('Connection Error', 'error');
        isScanning = false;
        playErrorSound();
    }
}

// Audio Feedback (optional - can be removed if not needed)
function playSuccessSound() {
    try {
        const audio = new Audio('data:audio/wav;base64,UklGRhQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=');
        audio.play().catch(() => {});
    } catch (e) {}
}

function playErrorSound() {
    try {
        const audio = new Audio('data:audio/wav;base64,UklGRhQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=');
        audio.play().catch(() => {});
    } catch (e) {}
}

// Event Listeners
if (retryBtn) {
    retryBtn.addEventListener('click', () => {
        hideResult();
        isScanning = false;
        startScanner();
    });
}

if (openDetailBtn) {
    openDetailBtn.addEventListener('click', () => {
        const url = openDetailBtn.dataset.redirect;
        if (url) {
            window.location.href = url;
        }
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && resultCard.style.display === 'block') {
        hideResult();
        isScanning = false;
        startScanner();
    }
    
    if (e.key === 'Enter' && openDetailBtn.style.display !== 'none') {
        openDetailBtn.click();
    }
});

// Page visibility - pause/resume scanner
document.addEventListener('visibilitychange', () => {
    if (document.hidden && qrScanner) {
        try {
            qrScanner.pause();
        } catch (e) {}
    } else if (!document.hidden && qrScanner && !isScanning) {
        try {
            qrScanner.resume();
        } catch (e) {
            startScanner();
        }
    }
});
