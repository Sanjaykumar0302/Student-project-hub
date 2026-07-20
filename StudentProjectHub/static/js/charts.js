function renderStatusChart(canvasId, labels, values) {
  const el = document.getElementById(canvasId);
  if (!el || typeof Chart === "undefined") return;

  new Chart(el, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: ["#E8A23B", "#202A52", "#5B33C4", "#2E9E63", "#3E7FBF", "#D95C5C"],
        borderWidth: 0,
      }],
    },
    options: {
      plugins: { legend: { position: "bottom", labels: { font: { family: "Inter" } } } },
      cutout: "62%",
    },
  });
}

function renderTypeChart(canvasId, labels, values) {
  const el = document.getElementById(canvasId);
  if (!el || typeof Chart === "undefined") return;

  new Chart(el, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Projects",
        data: values,
        backgroundColor: "#202A52",
        borderRadius: 6,
        maxBarThickness: 36,
      }],
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, ticks: { precision: 0 } },
      },
    },
  });
}
