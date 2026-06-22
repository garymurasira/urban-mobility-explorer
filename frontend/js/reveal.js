(function () {
  // .reveal is already in the markup (not added here) so the initial paint
  // starts hidden — adding the class via JS after first paint would cause
  // a visible flash from "shown" to "hidden" before the observer fires.
  const targets = document.querySelectorAll(".reveal");
  if (!targets.length || typeof IntersectionObserver === "undefined") {
    targets.forEach(function (el) {
      el.classList.add("is-visible");
    });
    return;
  }

  const observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  targets.forEach(function (el) {
    observer.observe(el);
  });
})();
