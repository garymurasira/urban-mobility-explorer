(function () {
  const grid = document.getElementById("kpi-grid");
  if (!grid) return;

  const CARDS = [
    { key: "total_trips", label: "Total trips", format: formatInt },
    { key: "avg_fare", label: "Avg fare", format: formatCurrency },
    { key: "avg_distance_mi", label: "Avg distance (mi)", format: formatDecimal },
    { key: "avg_duration_min", label: "Avg duration (min)", format: formatDecimal },
    { key: "pct_cross_borough", label: "Cross-borough trips", format: formatPercent },
  ];

  function formatInt(n) {
    return Number(n).toLocaleString("en-US");
  }

  function formatCurrency(n) {
    return "$" + Number(n).toFixed(2);
  }

  function formatDecimal(n) {
    return Number(n).toFixed(1);
  }

  function formatPercent(n) {
    return Number(n).toFixed(1) + "%";
  }

  function renderLoading() {
    grid.innerHTML = CARDS.map(function (card) {
      return (
        '<div class="kpi-card">' +
        '<p class="kpi-card__label">' + card.label + "</p>" +
        '<p class="kpi-card__value is-loading">Loading&hellip;</p>' +
        "</div>"
      );
    }).join("");
  }

  function renderSummary(summary) {
    grid.innerHTML = CARDS.map(function (card) {
      const value = summary[card.key];
      const display = value === undefined ? "&ndash;" : card.format(value);
      return (
        '<div class="kpi-card">' +
        '<p class="kpi-card__label">' + card.label + "</p>" +
        '<p class="kpi-card__value">' + display + "</p>" +
        "</div>"
      );
    }).join("");
  }

  function loadSummary(filters) {
    renderLoading();
    API.fetchSummary(filters)
      .then(renderSummary)
      .catch(function () {
        grid.innerHTML = '<p class="kpi-card__label">Could not load summary data.</p>';
      });
  }

  document.addEventListener("filters:change", function (event) {
    loadSummary(event.detail);
  });

  loadSummary({});
})();
