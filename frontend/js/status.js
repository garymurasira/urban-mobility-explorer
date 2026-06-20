/**
 * Shared helper for the "Loading…" / error text shown above charts,
 * the map, and insight cards while their data is in flight.
 */
function setStatus(el, text, isError) {
  if (!el) return;
  el.textContent = text || "";
  el.classList.toggle("is-visible", Boolean(text));
  el.classList.toggle("is-error", Boolean(isError));
}
