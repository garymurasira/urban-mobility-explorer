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
    const maxTrips = Math.max.apply(null, zones.map(function (z) { return z.trip_count; }));

    zones.forEach(function (zone) {
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
          "<tr>" +
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
    document.querySelectorAll("[data-sort-key]").forEach(function (th) {
      th.addEventListener("click", function () {
        const key = th.getAttribute("data-sort-key");
        if (sortKey === key) {
          sortDir = sortDir === "asc" ? "desc" : "asc";
        } else {
          sortKey = key;
          sortDir = "desc";
        }
        renderTable();
      });
    });
  }

  function load(filters) {
    setStatus(statusEl, "Loading zone data…");
    API.fetchTopZones(filters)
      .then(function (zones) {
        setStatus(statusEl, "");
        zonesData = zones;
        initMap();
        renderMarkers(zones);
        renderChart(zones);
        renderTable();
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
