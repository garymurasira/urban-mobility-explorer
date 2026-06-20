(function () {
  const form = document.getElementById("filter-bar");
  if (!form) return;

  const resetBtn = document.getElementById("filter-reset");

  function currentFilters() {
    const data = new FormData(form);
    const filters = {};
    data.forEach(function (value, key) {
      if (value) filters[key] = value;
    });
    return filters;
  }

  function emitChange() {
    document.dispatchEvent(
      new CustomEvent("filters:change", { detail: currentFilters() })
    );
  }

  form.addEventListener("change", emitChange);

  resetBtn.addEventListener("click", function () {
    form.reset();
    emitChange();
  });
})();
