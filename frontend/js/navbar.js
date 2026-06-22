(function () {
  const navbar = document.getElementById("navbar");
  const toggle = document.getElementById("navbar-toggle");
  const nav = document.getElementById("navbar-nav");

  if (!toggle || !nav) return;

  function setScrolledState() {
    if (navbar) navbar.classList.toggle("is-scrolled", window.scrollY > 8);
  }
  window.addEventListener("scroll", setScrolledState);
  setScrolledState();

  toggle.addEventListener("click", function () {
    const isOpen = nav.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
  });

  nav.querySelectorAll(".navbar__link").forEach(function (link) {
    link.addEventListener("click", function () {
      nav.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
    });
  });

  const links = nav.querySelectorAll(".navbar__link");
  const sections = Array.from(links).map(function (link) {
    return document.querySelector(link.getAttribute("href"));
  });

  function setActiveLinkOnScroll() {
    const scrollY = window.scrollY + 96;
    let activeIndex = 0;

    sections.forEach(function (section, index) {
      if (section && section.offsetTop <= scrollY) {
        activeIndex = index;
      }
    });

    links.forEach(function (link, index) {
      link.classList.toggle("is-active", index === activeIndex);
    });
  }

  window.addEventListener("scroll", setActiveLinkOnScroll);
  setActiveLinkOnScroll();
})();
