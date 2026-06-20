/**
 * API layer. Swap MOCK_MODE to false once David's Flask endpoints are live,
 * and point BASE_URL at the running backend.
 */
const API = (function () {
  const MOCK_MODE = true;
  const BASE_URL = "http://localhost:5000/api";

  const MOCK_SUMMARY = {
    total_trips: 1923841,
    avg_fare: 12.45,
    avg_distance_mi: 2.9,
    avg_duration_min: 14.2,
    pct_cross_borough: 18.6,
  };

  function fetchSummary(filters) {
    if (MOCK_MODE) {
      return Promise.resolve(MOCK_SUMMARY);
    }

    const params = new URLSearchParams(filters || {});
    return fetch(BASE_URL + "/stats/summary?" + params.toString()).then(
      function (res) {
        if (!res.ok) throw new Error("Failed to fetch summary");
        return res.json();
      }
    );
  }

  return { fetchSummary };
})();
