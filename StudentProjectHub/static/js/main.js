document.addEventListener("DOMContentLoaded", () => {
  // Auto-dismiss flash alerts after 5s
  document.querySelectorAll(".alert[data-auto-dismiss]").forEach((alertEl) => {
    setTimeout(() => {
      alertEl.classList.remove("show");
      alertEl.classList.add("fade");
      setTimeout(() => alertEl.remove(), 300);
    }, 5000);
  });
});
