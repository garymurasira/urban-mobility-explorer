/**
 * API layer — calls David's Flask backend directly. Point BASE_URL at
 * wherever the backend is actually running.
 *
 * Known backend gaps as of the latest pull (see message thread with
 * David): /api/zones/top has no lat/lon yet (zones.js skips plotting any
 * zone missing coordinates rather than crashing), and /api/stats/hourly +
 * /api/zones/top don't yet support the date/borough/payment filters —
 * sending them is harmless (ignored server-side) until that lands.
 */
const API = (function () {
  const BASE_URL = "http://localhost:5000/api";

  // NYC TLC's standard payment_type_id codes (data dictionary), used to
  // label David's /api/insights tips_by_payment rows for display.
  const PAYMENT_TYPE_LABELS = {
    1: "Credit card",
    2: "Cash",
    3: "No charge",
    4: "Dispute",
    5: "Unknown",
    6: "Voided trip",
  };

  function round(value, decimals) {
    const factor = Math.pow(10, decimals);
    return Math.round(value * factor) / factor;
  }

  function fetchSummary(filters) {
    // Backend now supports date_from/date_to/borough (matches the filter
    // bar's own param names) but not payment_type yet.
    const params = new URLSearchParams(filters || {});
    return fetch(BASE_URL + "/stats/summary?" + params.toString())
      .then(function (res) {
        if (!res.ok) throw new Error("Failed to fetch summary");
        return res.json();
      })
      .then(function (row) {
        return {
          total_trips: row.total_trips,
          avg_fare: row.avg_fare,
          avg_distance_mi: row.avg_trip_distance,
          avg_duration_min: row.avg_duration_min,
          pct_cross_borough: row.pct_cross_borough,
        };
      });
  }

  // Returns a flat array of { day_of_week, hour, trip_count } — one entry
  // per (day, hour) cell — for the Trends heatmap.
  function fetchHourly(filters) {
    const params = new URLSearchParams(filters || {});
    return fetch(BASE_URL + "/stats/hourly?" + params.toString())
      .then(function (res) {
        if (!res.ok) throw new Error("Failed to fetch hourly stats");
        return res.json();
      })
      .then(function (rows) {
        return rows.map(function (row) {
          return {
            day_of_week: row.day_of_week,
            hour: row.pickup_hour,
            trip_count: row.trip_count,
          };
        });
      });
  }

  function fetchTopZones(filters) {
    // Backend wraps results in {direction, limit, results}, not a bare
    // array — unwrap it here so callers just get the zone list.
    const params = new URLSearchParams(filters || {});
    return fetch(BASE_URL + "/zones/top?" + params.toString())
      .then(function (res) {
        if (!res.ok) throw new Error("Failed to fetch top zones");
        return res.json();
      })
      .then(function (payload) {
        return payload.results || [];
      });
  }

  // David's /api/insights returns raw aggregates, not display copy — we
  // write the interpretive text ourselves so we control the storytelling.
  function buildInsightCards(raw) {
    const cards = [];

    if (raw.peak_hour) {
      cards.push({
        title: "Demand peaks at a single hour",
        stat: raw.peak_hour.pickup_hour + ":00",
        body:
          "The busiest pickup hour citywide is " + raw.peak_hour.pickup_hour +
          ":00, with " + Number(raw.peak_hour.trip_count).toLocaleString("en-US") +
          " trips recorded in that hour alone across the month.",
      });
    }

    if (raw.cross_borough && raw.cross_borough.total_trips) {
      const pct = round(
        (raw.cross_borough.cross_trips / raw.cross_borough.total_trips) * 100,
        1
      );
      cards.push({
        title: "Most trips stay within one borough",
        stat: pct + "%",
        body:
          "Only " + pct + "% of trips cross a borough line — the rest start " +
          "and end in the same borough, suggesting most demand is local " +
          "rather than cross-city.",
      });
    }

    if (raw.tips_by_payment && raw.tips_by_payment.length) {
      const top = raw.tips_by_payment[0];
      const label = PAYMENT_TYPE_LABELS[top.payment_type_id] || "this payment type";
      cards.push({
        title: "Tipping behavior varies by payment method",
        stat: round(top.avg_tip_pct * 100, 1) + "%",
        body:
          label + " trips have the highest average tip percentage, at " +
          round(top.avg_tip_pct * 100, 1) + "% of the fare.",
      });
    }

    return cards;
  }

  function fetchInsights(filters) {
    const params = new URLSearchParams(filters || {});
    return fetch(BASE_URL + "/insights?" + params.toString())
      .then(function (res) {
        if (!res.ok) throw new Error("Failed to fetch insights");
        return res.json();
      })
      .then(buildInsightCards);
  }

  // /api/trips exists on the backend (paginated, sortable trip rows) but
  // nothing in the dashboard calls it yet. Added for when we build a raw
  // trips table/drill-down view. NOTE: its filter params use different
  // names/types than the filter bar (start_date/end_date, payment_type as
  // an integer id) — pass backend-shaped params, not filter-bar filters,
  // until that's standardized.
  function fetchTrips(backendParams) {
    const params = new URLSearchParams(backendParams || {});
    return fetch(BASE_URL + "/trips?" + params.toString()).then(function (res) {
      if (!res.ok) throw new Error("Failed to fetch trips");
      return res.json();
    });
  }

  return { fetchSummary, fetchHourly, fetchTopZones, fetchInsights, fetchTrips };
})();
