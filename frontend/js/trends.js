(function () {
  const canvas = document.getElementById("hourly-chart");
  if (!canvas || typeof Chart === "undefined") return;

  let chart = null;

  function render(hourly) {
    const labels = hourly.map(function (row) {
      return row.hour + ":00";
    });
    const data = hourly.map(function (row) {
      return row.trip_count;
    });

    if (chart) {
      chart.data.labels = labels;
      chart.data.datasets[0].data = data;
      chart.update();
      return;
    }

    chart = new Chart(canvas, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Trips",
            data: data,
            backgroundColor: "#F5C518",
            borderRadius: 4,
            maxBarThickness: 28,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, ticks: { callback: function (v) { return v / 1000 + "k"; } } },
        },
      },
    });
  }

  function load(filters) {
    API.fetchHourly(filters).then(render);
  }

  document.addEventListener("filters:change", function (event) {
    load(event.detail);
  });

  load({});
})();
