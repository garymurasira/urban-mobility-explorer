(function () {
  const grid = document.getElementById("hourly-heatmap");
  const statusEl = document.getElementById("trends-status");
  if (!grid) return;

  const DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const HOUR_LABELS = [0, 3, 6, 9, 12, 15, 18, 21];

  function colorFor(value, max) {
    if (max === 0) return "rgba(245, 197, 24, 0.06)";
    const opacity = 0.08 + (value / max) * 0.85;
    return "rgba(245, 197, 24, " + opacity.toFixed(2) + ")";
  }

  function render(cells) {
    const byDay = {};
    let max = 0;

    cells.forEach(function (cell) {
      byDay[cell.day_of_week] = byDay[cell.day_of_week] || {};
      byDay[cell.day_of_week][cell.hour] = cell.trip_count;
      if (cell.trip_count > max) max = cell.trip_count;
    });

    // Every cell gets an explicit grid-row/grid-column. Mixing explicit
    // placement (the hour header) with auto-placed day rows made the grid
    // auto-placement algorithm dodge the header's occupied cells, which
    // fragmented and misaligned the day rows on narrow screens.
    const hourHeader = HOUR_LABELS.map(function (h) {
      return (
        '<span class="heatmap__hour-label" style="grid-row:1;grid-column:' +
        (h + 2) + '">' + h + ":00</span>"
      );
    }).join("");

    const rows = DAY_LABELS.map(function (label, dayIndex) {
      const row = dayIndex + 2;
      const dayLabel =
        '<span class="heatmap__day-label" style="grid-row:' + row + ';grid-column:1">' +
        label + "</span>";

      const cellsHtml = Array.from({ length: 24 }, function (_, hour) {
        const value = (byDay[dayIndex] && byDay[dayIndex][hour]) || 0;
        const title = label + " " + hour + ":00 — " + value.toLocaleString("en-US") + " trips";
        return (
          '<div class="heatmap__cell" style="grid-row:' + row + ";grid-column:" + (hour + 2) +
          ";background:" + colorFor(value, max) + '" title="' + title + '"></div>'
        );
      }).join("");

      return dayLabel + cellsHtml;
    }).join("");

    grid.innerHTML = hourHeader + rows;
  }

  function load(filters) {
    setStatus(statusEl, "Loading hourly trends…");
    API.fetchHourly(filters)
      .then(function (cells) {
        setStatus(statusEl, "");
        render(cells);
      })
      .catch(function () {
        setStatus(statusEl, "Could not load hourly trends. Try again later.", true);
      });
  }

  document.addEventListener("filters:change", function (event) {
    load(event.detail);
  });

  load({});
})();
