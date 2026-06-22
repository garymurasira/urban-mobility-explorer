(function () {
  const mapEl = document.getElementById("zones-map");
  const chartCanvas = document.getElementById("zones-chart");
  const tableBody = document.getElementById("zones-table-body");
  const statusEl = document.getElementById("zones-status");
  if (!mapEl && !chartCanvas && !tableBody) return;

  let map = null;
  let markersLayer = null;
  let chart = null;
  let zonesData = [];
  let sortKey = "trip_count";
  let sortDir = "desc";

  function initMap() {
    if (map || typeof L === "undefined" || !mapEl) return;
    map = L.map(mapEl).setView([40.7128, -73.95], 10.5);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
      maxZoom: 17,
    }).addTo(map);
    markersLayer = L.layerGroup().addTo(map);
  }

  function renderMarkers(zones) {
    if (!map) return;
    markersLayer.clearLayers();

    // David's /api/zones/top doesn't include lat/lon yet (flagged to him).
    // Skip plotting any zone we don't have coordinates for instead of
    // letting Leaflet throw on an invalid LatLng.
    const plottable = zones.filter(function (z) {
      return typeof z.lat === "number" && typeof z.lon === "number";
    });
    if (plottable.length === 0) return;

    const maxTrips = Math.max.apply(null, plottable.map(function (z) { return z.trip_count; }));

    plottable.forEach(function (zone) {
      const radius = 6 + (zone.trip_count / maxTrips) * 18;
      L.circleMarker([zone.lat, zone.lon], {
        radius: radius,
        color: "#D9A900",
        fillColor: "#F5C518",
        fillOpacity: 0.6,
        weight: 1,
      })
        .bindPopup(
          "<strong>" + zone.zone + "</strong><br>" +
          zone.borough + "<br>" +
          zone.trip_count.toLocaleString("en-US") + " trips"
        )
        .addTo(markersLayer);
    });
  }

  function renderChart(zones) {
    if (!chartCanvas || typeof Chart === "undefined") return;
    const top = zones.slice(0, 7);
    const labels = top.map(function (z) { return z.zone; });
    const data = top.map(function (z) { return z.trip_count; });

    if (chart) {
      chart.data.labels = labels;
      chart.data.datasets[0].data = data;
      chart.update();
      return;
    }

    chart = new Chart(chartCanvas, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Trips",
            data: data,
            backgroundColor: "#F5C518",
            borderRadius: 4,
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true } },
      },
    });
  }

  function renderTable() {
    if (!tableBody) return;
    const sorted = zonesData.slice().sort(function (a, b) {
      const diff = a[sortKey] > b[sortKey] ? 1 : a[sortKey] < b[sortKey] ? -1 : 0;
      return sortDir === "asc" ? diff : -diff;
    });

    tableBody.innerHTML = sorted
      .map(function (zone, index) {
        return (
          '<tr style="animation-delay:' + Math.min(index * 30, 300) + 'ms">' +
          '<td class="zone-table__rank">' + (index + 1) + "</td>" +
          "<td>" + zone.zone + "</td>" +
          "<td>" + zone.borough + "</td>" +
          "<td>" + zone.trip_count.toLocaleString("en-US") + "</td>" +
          "</tr>"
        );
      })
      .join("");
  }

  function bindSortHeaders() {
    const headers = document.querySelectorAll("[data-sort-key]");

    function activate(th) {
      const key = th.getAttribute("data-sort-key");
      if (sortKey === key) {
        sortDir = sortDir === "asc" ? "desc" : "asc";
      } else {
        sortKey = key;
        sortDir = "desc";
      }

      headers.forEach(function (h) {
        h.setAttribute(
          "aria-sort",
          h.getAttribute("data-sort-key") === sortKey
            ? (sortDir === "asc" ? "ascending" : "descending")
            : "none"
        );
      });

      renderTable();
    }

    headers.forEach(function (th) {
      th.addEventListener("click", function () {
        activate(th);
      });
      th.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          activate(th);
        }
      });
    });
  }

  function load(filters) {
    setStatus(statusEl, "Loading zone data…");
    API.fetchTopZones(filters)
      .then(function (zones) {
        zonesData = zones;
        initMap();
        renderMarkers(zones);
        renderChart(zones);
        renderTable();

        if (zones.length === 0) {
          setStatus(statusEl, "No zones match the current filters.");
        } else {
          setStatus(statusEl, "");
        }
      })
      .catch(function () {
        setStatus(statusEl, "Could not load zone data. Try again later.", true);
      });
  }

  document.addEventListener("filters:change", function (event) {
    load(event.detail);
  });

  bindSortHeaders();
  load({});
})();
