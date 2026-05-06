/* =====================================================
   VMS – PREMIUM AMBIENT MOTION (FINAL)
   ===================================================== */

let idleTimeout;

document.addEventListener("mousemove", (e) => {
    const container = document.querySelector(".index-container");
    if (!container) return;

    clearTimeout(idleTimeout);

    const x = (e.clientX / window.innerWidth - 0.5) * 30;
    const y = (e.clientY / window.innerHeight - 0.5) * 30;

    container.style.setProperty("--ambient-x", `${x}px`);
    container.style.setProperty("--ambient-y", `${y}px`);

    /* Reset to idle motion after user stops */
    idleTimeout = setTimeout(() => {
        container.style.setProperty("--ambient-x", `0px`);
        container.style.setProperty("--ambient-y", `0px`);
    }, 1200);
});

