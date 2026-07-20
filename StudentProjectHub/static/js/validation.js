document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form[data-validate]").forEach((form) => {
    form.addEventListener("submit", (e) => {
      let valid = true;
      form.querySelectorAll("[required]").forEach((field) => {
        if (!field.value || !field.value.trim()) {
          valid = false;
          field.classList.add("is-invalid");
        } else {
          field.classList.remove("is-invalid");
        }
      });

      const pw = form.querySelector("[data-password]");
      const confirmPw = form.querySelector("[data-confirm-password]");
      if (pw && confirmPw && pw.value !== confirmPw.value) {
        valid = false;
        confirmPw.classList.add("is-invalid");
      }

      if (!valid) {
        e.preventDefault();
      }
    });
  });
});
