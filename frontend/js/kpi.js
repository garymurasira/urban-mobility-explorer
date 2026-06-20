(function () {
  const grid = document.getElementById("kpi-grid");
  if (!grid) return;

  const ICON_PATHS = {
    trips: '<path d="M3 17h18M5 17V9a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v8M7 7l1-3h8l1 3"/><circle cx="7.5" cy="17" r="1.5"/><circle cx="16.5" cy="17" r="1.5"/>',
    fare: '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2 2 0 0 1 2-1.6h1a1.8 1.8 0 0 1 0 3.6h-1a1.8 1.8 0 0 0 0 3.6h1a2 2 0 0 0 2-1.6M12 6.5v1M12 16v1"/>',
    distance: '<path d="M3 6h12M3 12h18M3 18h8"/><circle cx="19" cy="6" r="2"/><circle cx="9" cy="18" r="2"/>',
    duration: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    cross: '<path d="M7 7h10l-3-3M17 17H7l3 3"/>',
  };

  function icon(name) {
    return (
      '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" ' +
      'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
      ICON_PATHS[name] +
      "</svg>"
    );
  }

  const CARDS = [
    { key: "total_trips", label: "Total trips", icon: "trips", format: formatInt },
    { key: "avg_fare", label: "Avg fare", icon: "fare", format: formatCurrency },
    { key: "avg_distance_mi", label: "Avg distance (mi)", icon: "distance", format: formatDecimal },
    { key: "avg_duration_min", label: "Avg duration (min)", icon: "duration", format: formatDecimal },
    { key: "pct_cross_borough", label: "Cross-borough trips", icon: "cross", format: formatPercent },
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
        '<div class="kpi-card__icon">' + icon(card.icon) + "</div>" +
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
        '<div class="kpi-card__icon">' + icon(card.icon) + "</div>" +
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
