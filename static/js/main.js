// main.js — students will add JavaScript here as features are built

document.addEventListener("DOMContentLoaded", () => {
    const openers = document.querySelectorAll("[data-modal-open]");
    const closers = document.querySelectorAll("[data-modal-close]");

    function openModal(id) {
        const modal = document.getElementById(id);
        if (!modal) return;

        const iframe = modal.querySelector("[data-modal-video]");
        if (iframe && !iframe.src) {
            // Lazy-load the YouTube embed only when opened.
            // Replace the URL below with your real video.
            iframe.src = "https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1&rel=0";
        }

        modal.hidden = false;
        modal.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";
    }

    function closeModal(modal) {
        const iframe = modal.querySelector("[data-modal-video]");
        // Clearing src fully stops playback and unloads the player.
        if (iframe) iframe.src = "";

        modal.hidden = true;
        modal.setAttribute("aria-hidden", "true");
        document.body.style.overflow = "";
    }

    openers.forEach((btn) => {
        btn.addEventListener("click", () => openModal(btn.dataset.modalOpen));
    });

    closers.forEach((btn) => {
        btn.addEventListener("click", () => {
            const modal = btn.closest(".modal");
            if (modal) closeModal(modal);
        });
    });

    document.addEventListener("keydown", (e) => {
        if (e.key !== "Escape") return;
        document.querySelectorAll(".modal:not([hidden])").forEach(closeModal);
    });
});
