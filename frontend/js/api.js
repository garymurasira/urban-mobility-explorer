/**
 * API layer. Swap MOCK_MODE to false once David's Flask endpoints are live,
 * and point BASE_URL at the running backend.
 */
const API = (function () {
  const MOCK_MODE = true;
  const BASE_URL = "http://localhost:5000/api";

  // Figures grounded in Espoir's cleaned dataset (7,485,597 trips total;
  // see docs/report_problem_framing_espoir.md) and the 1,000-row cleaned
  // sample (data/sample/trips_clean_sample.csv) for the per-trip averages.
  const MOCK_SUMMARY = {
    total_trips: 7485597,
    avg_fare: 12.43,
    avg_distance_mi: 2.86,
    avg_duration_min: 14.47,
    pct_cross_borough: 10.71,
  };

  // Hour-of-day shapes for a weekday (commute peaks) vs a weekend (flatter,
  // later peak), used to synthesize a plausible day_of_week x hour grid.
  // day_of_week follows pandas .dt.dayofweek: 0=Mon .. 6=Sun.
  const WEEKDAY_HOURLY = [
    18, 11, 7, 5, 6, 14, 38, 72, 95, 70, 58, 62, 68, 64, 60, 66, 78, 98, 100,
    82, 60, 45, 33, 24,
  ];
  const WEEKEND_HOURLY = [
    25, 18, 12, 8, 6, 5, 8, 15, 25, 40, 55, 68, 75, 80, 82, 85, 88, 90, 88,
    80, 65, 50, 38, 28,
  ];

  const MOCK_HEATMAP = [];
  for (let day = 0; day < 7; day++) {
    const pattern = day < 5 ? WEEKDAY_HOURLY : WEEKEND_HOURLY;
    const dayFactor = day < 5 ? 1 : 0.8;
    pattern.forEach(function (count, hour) {
      MOCK_HEATMAP.push({
        day_of_week: day,
        hour: hour,
        trip_count: Math.round(count * 1000 * dayFactor),
      });
    });
  }

  const MOCK_TOP_ZONES = [
    { zone: "Midtown Center", borough: "Manhattan", trip_count: 184320, lat: 40.7549, lon: -73.984 },
    { zone: "Upper East Side South", borough: "Manhattan", trip_count: 162110, lat: 40.7736, lon: -73.9566 },
    { zone: "JFK Airport", borough: "Queens", trip_count: 151870, lat: 40.6413, lon: -73.7781 },
    { zone: "Times Sq/Theatre District", borough: "Manhattan", trip_count: 147600, lat: 40.759, lon: -73.9845 },
    { zone: "LaGuardia Airport", borough: "Queens", trip_count: 121430, lat: 40.7769, lon: -73.874 },
    { zone: "East Village", borough: "Manhattan", trip_count: 98340, lat: 40.7265, lon: -73.9815 },
    { zone: "Park Slope", borough: "Brooklyn", trip_count: 64210, lat: 40.6710, lon: -73.9814 },
  ];

  // Computed from data/sample/trips_clean_sample.csv (1,000-row cleaned
  // sample) joined to zones_reference.csv. Re-derive from the full 7.48M
  // row table once the live DB/API is connected — these are directional,
  // not final, figures.
  const MOCK_INSIGHTS = [
    {
      title: "Manhattan dominates pickup demand",
      stat: "90.5%",
      body:
        "90.5% of sampled pickups originate in Manhattan, versus 6.2% in " +
        "Queens and just over 1% in Brooklyn — demand is heavily " +
        "concentrated in a small footprint of the city.",
    },
    {
      title: "Most trips stay within one borough",
      stat: "11.8%",
      body:
        "Only 11.8% of sampled trips cross a borough line (full-dataset " +
        "figure: 10.71%, per the cleaning report) — the large majority of " +
        "demand is short, local movement rather than cross-borough travel.",
    },
    {
      title: "Night trips cost more than any other time of day",
      stat: "+23%",
      body:
        "Night trips average $14.75 versus $11.96 for the rest of the day " +
        "— about 23% higher — consistent with the TLC's mandated overnight " +
        "surcharge (8pm-6am), not just lighter traffic.",
    },
  ];

  // Rough share of citywide pickups per borough, used only to make mock
  // filtering feel plausible until the real API supplies real numbers.
  const BOROUGH_SHARE = {
    Manhattan: 0.62,
    Brooklyn: 0.18,
    Queens: 0.15,
    Bronx: 0.03,
    "Staten Island": 0.02,
  };

  const PAYMENT_FARE_FACTOR = { card: 1.05, cash: 0.85, other: 0.95 };

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

  function daysInRange(filters) {
    if (!filters.date_from && !filters.date_to) return 31;
    const from = filters.date_from ? new Date(filters.date_from) : new Date("2019-01-01");
    const to = filters.date_to ? new Date(filters.date_to) : new Date("2019-01-31");
    const spanMs = to - from;
    if (Number.isNaN(spanMs) || spanMs < 0) return 31;
    return Math.min(31, Math.round(spanMs / 86400000) + 1);
  }

  function round(value, decimals) {
    const factor = Math.pow(10, decimals);
    return Math.round(value * factor) / factor;
  }

  function fetchSummary(filters) {
    if (MOCK_MODE) {
      filters = filters || {};
      const dayFraction = daysInRange(filters) / 31;
      const boroughShare = filters.borough ? BOROUGH_SHARE[filters.borough] || 0.05 : 1;
      const fareFactor = filters.payment_type ? PAYMENT_FARE_FACTOR[filters.payment_type] || 1 : 1;

      return Promise.resolve({
        total_trips: Math.round(MOCK_SUMMARY.total_trips * dayFraction * boroughShare),
        avg_fare: round(MOCK_SUMMARY.avg_fare * fareFactor, 2),
        avg_distance_mi: MOCK_SUMMARY.avg_distance_mi,
        avg_duration_min: MOCK_SUMMARY.avg_duration_min,
        pct_cross_borough: round(
          MOCK_SUMMARY.pct_cross_borough * (filters.borough ? 0.5 : 1),
          1
        ),
      });
    }

    // NOTE: backend ignores filters today (no WHERE clause in
    // stats.py:summary) and has no pct_cross_borough — flagged to David.
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
    if (MOCK_MODE) {
      filters = filters || {};
      const dayFraction = daysInRange(filters) / 31;
      const boroughShare = filters.borough ? BOROUGH_SHARE[filters.borough] || 0.05 : 1;
      const scale = dayFraction * boroughShare;

      return Promise.resolve(
        MOCK_HEATMAP.map(function (row) {
          return {
            day_of_week: row.day_of_week,
            hour: row.hour,
            trip_count: Math.round(row.trip_count * scale),
          };
        })
      );
    }

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
    if (MOCK_MODE) {
      filters = filters || {};
      const dayFraction = daysInRange(filters) / 31;
      const zones = MOCK_TOP_ZONES.filter(function (zone) {
        return !filters.borough || zone.borough === filters.borough;
      }).map(function (zone) {
        return { ...zone, trip_count: Math.round(zone.trip_count * dayFraction) };
      });

      return Promise.resolve(zones);
    }

    // Backend wraps results in {direction, limit, results}, not a bare
    // array, and doesn't include lat/lon yet — flagged to David.
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
    if (MOCK_MODE) {
      return Promise.resolve(MOCK_INSIGHTS);
    }

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
    if (MOCK_MODE) {
      return Promise.resolve({
        page: 1,
        page_size: 25,
        total: 0,
        total_pages: 0,
        sort_by: "pickup_datetime",
        order: "desc",
        data: [],
      });
    }

    const params = new URLSearchParams(backendParams || {});
    return fetch(BASE_URL + "/trips?" + params.toString()).then(function (res) {
      if (!res.ok) throw new Error("Failed to fetch trips");
      return res.json();
    });
  }

  return { fetchSummary, fetchHourly, fetchTopZones, fetchInsights, fetchTrips };
})();
