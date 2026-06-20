(function () {
  const grid = document.getElementById("insights-grid");
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

  API.fetchInsights({}).then(render);
})();
