document.addEventListener("DOMContentLoaded", function () {

    /* ===============================
       OTP INPUT HANDLING
    =============================== */

    const inputs = document.querySelectorAll(".otp-box");
    const hiddenInput = document.getElementById("otp-combined");

    if (inputs.length > 0) {
        inputs[0].focus();
    }

    inputs.forEach((input, index) => {

        input.addEventListener("input", () => {
            input.value = input.value.replace(/[^0-9]/g, "");

            if (input.value.length > 1) {
                input.value = input.value.charAt(0);
            }

            if (input.value.length === 1 && index < inputs.length - 1) {
                inputs[index + 1].focus();
            }

            updateHiddenOTP();
        });

        input.addEventListener("keydown", (e) => {
            if (e.key === "Backspace" && input.value === "" && index > 0) {
                inputs[index - 1].focus();
            }
        });
    });

    const otpContainer = document.querySelector(".otp-inputs");

    otpContainer.addEventListener("paste", function (e) {
        e.preventDefault();
        const pastedData = e.clipboardData.getData("text").trim();

        if (!/^\d{6}$/.test(pastedData)) return;

        pastedData.split("").forEach((digit, i) => {
            if (inputs[i]) inputs[i].value = digit;
        });

        inputs[5].focus();
        updateHiddenOTP();
    });

    function updateHiddenOTP() {
        let otp = "";
        inputs.forEach(input => otp += input.value);
        hiddenInput.value = otp;
    }


    /* ===============================
       RESEND OTP WITH AUTO TIMER
    =============================== */

    const resendBtn = document.getElementById("resend-btn");
    const countdownEl = document.getElementById("countdown");

    if (!resendBtn) return;

    const resendUrl = resendBtn.getAttribute("data-url");

    let timer = 30;
    let interval = null;

    function startCountdown() {

        resendBtn.disabled = true;
        timer = 30;

        countdownEl.innerText = ` (30s)`;

        interval = setInterval(() => {
            timer--;
            countdownEl.innerText = ` (${timer}s)`;

            if (timer <= 0) {
                clearInterval(interval);
                resendBtn.disabled = false;
                countdownEl.innerText = "";
            }
        }, 1000);
    }

    // 🔥 START TIMER IMMEDIATELY ON PAGE LOAD
    startCountdown();


    resendBtn.addEventListener("click", function () {

        if (resendBtn.disabled) return;

        // Grab visit_id from the hidden input as a fallback
        const visitIdInput = document.querySelector('input[name="visit_id"]');
        const visitId = visitIdInput ? visitIdInput.value : '';

        fetch(resendUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ visit_id: visitId }) // Add visit_id to body
        })
        .then(response => response.json())
        .then(data => {

            if (data.success) {

                clearInterval(interval);
                startCountdown();

                showToast("New OTP sent to your email.");

            } else {

                showToast(data.message, true);

            }
        })
        .catch(() => {
            showToast("Something went wrong. Please try again.", true);
        });

    });


    /* ===============================
       CLEAN TOAST MESSAGE
    =============================== */

    function showToast(message, isError = false) {

        let toast = document.createElement("div");
        toast.className = "otp-toast";
        toast.innerText = message;

        if (isError) {
            toast.style.background = "#ef4444";
        }

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

});
