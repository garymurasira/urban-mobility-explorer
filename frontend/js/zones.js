(function () {
  const mapEl = document.getElementById("zones-map");
  const mapLegend = document.getElementById("zones-map-legend");
  const chartCanvas = document.getElementById("zones-chart");
  const tableBody = document.getElementById("zones-table-body");
  const statusEl = document.getElementById("zones-status");
  if (!mapEl && !chartCanvas && !tableBody) return;

  let map = null;
  let markersLayer = null;
  let choroplethLayer = null;
  let zonesGeoJson = null;
  let chart = null;
  let zonesData = [];
  let sortKey = "trip_count";
  let sortDir = "desc";

  // Same cream -> gold -> deep amber scale as the Trends heatmap, so the
  // two visualizations read consistently across the dashboard.
  const SCALE_STOPS = [
    [255, 251, 235],
    [245, 197, 24],
    [180, 83, 9],
  ];
  const NO_DATA_FILL = "#EFEFEF";

  function lerp(a, b, t) {
    return Math.round(a + (b - a) * t);
  }

  function colorAt(t) {
    t = Math.max(0, Math.min(1, t));
    const segment = t < 0.5 ? 0 : 1;
    const localT = t < 0.5 ? t / 0.5 : (t - 0.5) / 0.5;
    const from = SCALE_STOPS[segment];
    const to = SCALE_STOPS[segment + 1];
    return "rgb(" + [
      lerp(from[0], to[0], localT),
      lerp(from[1], to[1], localT),
      lerp(from[2], to[2], localT),
    ].join(",") + ")";
  }

  function initMap() {
    if (map || typeof L === "undefined" || !mapEl) return;
    map = L.map(mapEl).setView([40.7128, -73.95], 10.5);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
      maxZoom: 17,
    }).addTo(map);

    fetch("assets/zones.geojson")
      .then(function (res) { return res.json(); })
      .then(function (geojson) {
        zonesGeoJson = geojson;
        renderChoropleth(zonesData);
      })
      .catch(function () {
        // Choropleth is a visual enhancement, not critical — badges/chart/
        // table still work fine without it if the asset fails to load.
      });

    markersLayer = L.layerGroup().addTo(map);
  }

  function renderChoropleth(zones) {
    if (!map || !zonesGeoJson) return;

    const byLocationId = {};
    zones.forEach(function (z) {
      if (z.location_id != null) byLocationId[z.location_id] = z.trip_count;
    });
    const max = Math.max.apply(null, zones.map(function (z) { return z.trip_count; }).concat(0));

    if (choroplethLayer) {
      map.removeLayer(choroplethLayer);
    }

    choroplethLayer = L.geoJSON(zonesGeoJson, {
      style: function (feature) {
        const tripCount = byLocationId[feature.properties.location_id];
        const hasData = typeof tripCount === "number";
        return {
          fillColor: hasData ? colorAt(Math.sqrt(tripCount / max)) : NO_DATA_FILL,
          fillOpacity: hasData ? 0.75 : 0.35,
          color: "#FFFFFF",
          weight: 1,
        };
      },
      onEachFeature: function (feature, layer) {
        const tripCount = byLocationId[feature.properties.location_id];
        const label =
          "<strong>" + feature.properties.zone + "</strong><br>" +
          feature.properties.borough + "<br>" +
          (typeof tripCount === "number"
            ? tripCount.toLocaleString("en-US") + " trips"
            : "No trip data for this zone");
        layer.bindPopup(label);
      },
    }).addTo(map);

    choroplethLayer.bringToBack();
    renderMapLegend();
  }

  function renderMapLegend() {
    if (!mapLegend || mapLegend.dataset.rendered) return;
    const swatches = [0, 0.25, 0.5, 0.75, 1]
      .map(function (t) {
        return '<span class="heatmap-legend__swatch" style="background:' + colorAt(t) + '"></span>';
      })
      .join("");
    mapLegend.innerHTML =
      '<span class="heatmap-legend__swatch" style="background:' + NO_DATA_FILL + '"></span>' +
      '<span class="heatmap-legend__label">No data</span>' +
      swatches +
      '<span class="heatmap-legend__label">More trips</span>';
    mapLegend.dataset.rendered = "true";
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

    // Small circle markers were too easy to lose against the basemap's own
    // road shields/labels. Numbered badge pins (matching the table's rank
    // column) are bigger and easier to actually see and tell apart.
    const ranked = plottable.slice().sort(function (a, b) {
      return b.trip_count - a.trip_count;
    });

    ranked.forEach(function (zone, index) {
      const icon = L.divIcon({
        className: "zone-pin",
        html: '<span class="zone-pin__badge">' + (index + 1) + "</span>",
        iconSize: [30, 30],
        iconAnchor: [15, 15],
      });

      L.marker([zone.lat, zone.lon], { icon: icon })
        .bindPopup(
          "<strong>#" + (index + 1) + " " + zone.zone + "</strong><br>" +
          zone.borough + "<br>" +
          zone.trip_count.toLocaleString("en-US") + " trips"
        )
        .bindTooltip(zone.zone, { direction: "top", offset: [0, -16] })
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
            barPercentage: 0.6,
            categoryPercentage: 0.7,
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
        renderChoropleth(zones);
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
