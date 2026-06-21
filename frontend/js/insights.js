(function () {
  const grid = document.getElementById("insights-grid");
  const statusEl = document.getElementById("insights-status");
  if (!grid) return;

  function render(insights) {
    grid.innerHTML = insights
      .map(function (insight) {
        return (
          '<div class="insight-card">' +
          '<p class="insight-card__stat">' + insight.stat + "</p>" +
          '<h3 class="insight-card__title">' + insight.title + "</h3>" +
          '<p class="insight-card__body">' + insight.body + "</p>" +
          "</div>"
        );
      })
      .join("");
  }

  setStatus(statusEl, "Loading insights…");
  API.fetchInsights({})
    .then(function (insights) {
      setStatus(statusEl, "");
      render(insights);
    })
    .catch(function () {
      setStatus(statusEl, "Could not load insights. Try again later.", true);
    });
})();
