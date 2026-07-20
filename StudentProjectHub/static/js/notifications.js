document.addEventListener("DOMContentLoaded", () => {
  const countBadge = document.querySelector("[data-unread-count]");

  const refreshCount = () => {
    if (!countBadge) return;
    fetch("/notifications/unread-count")
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (!data) return;
        if (data.count > 0) {
          countBadge.textContent = data.count > 9 ? "9+" : data.count;
          countBadge.style.display = "flex";
        } else {
          countBadge.style.display = "none";
        }
      })
      .catch(() => {});
  };

  // Refresh every 30s while the tab is open
  if (countBadge) {
    setInterval(refreshCount, 30000);
  }
});
