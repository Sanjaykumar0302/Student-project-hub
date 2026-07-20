document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-upload-drop]").forEach((dropZone) => {
    const input = dropZone.querySelector("input[type=file]");
    const chipHolder = dropZone.querySelector("[data-file-chip]");
    if (!input) return;

    const showChip = (file) => {
      if (!chipHolder) return;
      chipHolder.innerHTML = file
        ? `<span class="file-chip">📎 ${file.name}</span>`
        : "";
    };

    input.addEventListener("change", () => {
      showChip(input.files && input.files[0]);
    });

    ["dragenter", "dragover"].forEach((evt) => {
      dropZone.addEventListener(evt, (e) => {
        e.preventDefault();
        dropZone.classList.add("dragging");
      });
    });

    ["dragleave", "drop"].forEach((evt) => {
      dropZone.addEventListener(evt, (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragging");
      });
    });

    dropZone.addEventListener("drop", (e) => {
      if (e.dataTransfer.files.length) {
        input.files = e.dataTransfer.files;
        showChip(e.dataTransfer.files[0]);
      }
    });
  });
});
