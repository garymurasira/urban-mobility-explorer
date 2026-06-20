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

  // Trip counts by hour-of-day, shaped like the morning/evening commute peaks.
  const MOCK_HOURLY = [
    18, 11, 7, 5, 6, 14, 38, 72, 95, 70, 58, 62, 68, 64, 60, 66, 78, 98, 100,
    82, 60, 45, 33, 24,
  ].map(function (count, hour) {
    return { hour: hour, trip_count: count * 1000 };
  });

  const MOCK_TOP_ZONES = [
    { zone: "Midtown Center", borough: "Manhattan", trip_count: 184320, lat: 40.7549, lon: -73.984 },
    { zone: "Upper East Side South", borough: "Manhattan", trip_count: 162110, lat: 40.7736, lon: -73.9566 },
    { zone: "JFK Airport", borough: "Queens", trip_count: 151870, lat: 40.6413, lon: -73.7781 },
    { zone: "Times Sq/Theatre District", borough: "Manhattan", trip_count: 147600, lat: 40.759, lon: -73.9845 },
    { zone: "LaGuardia Airport", borough: "Queens", trip_count: 121430, lat: 40.7769, lon: -73.874 },
    { zone: "East Village", borough: "Manhattan", trip_count: 98340, lat: 40.7265, lon: -73.9815 },
    { zone: "Park Slope", borough: "Brooklyn", trip_count: 64210, lat: 40.6710, lon: -73.9814 },
  ];

  const MOCK_INSIGHTS = [
    {
      title: "Manhattan dominates demand",
      stat: "78%",
      body:
        "78% of all pickups originate in Manhattan, even though it holds " +
        "only a third of the zone count — demand is heavily concentrated " +
        "in a small footprint of the city.",
    },
    {
      title: "Evening rush outprices the morning",
      stat: "+22%",
      body:
        "Average fares between 5-7pm run about 22% higher than the 8-9am " +
        "morning peak, despite similar trip volumes — likely a mix of " +
        "longer evening trips and congestion surcharges.",
    },
    {
      title: "Airport trips are the outliers",
      stat: "2.4x",
      body:
        "Trips to/from JFK and LaGuardia average 2.4x the fare of a typical " +
        "in-borough trip and skew the city-wide average distance upward.",
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

    const params = new URLSearchParams(filters || {});
    return fetch(BASE_URL + "/stats/summary?" + params.toString()).then(
      function (res) {
        if (!res.ok) throw new Error("Failed to fetch summary");
        return res.json();
      }
    );
  }

  function fetchHourly(filters) {
    if (MOCK_MODE) {
      filters = filters || {};
      const dayFraction = daysInRange(filters) / 31;
      const boroughShare = filters.borough ? BOROUGH_SHARE[filters.borough] || 0.05 : 1;
      const scale = dayFraction * boroughShare;

      return Promise.resolve(
        MOCK_HOURLY.map(function (row) {
          return { hour: row.hour, trip_count: Math.round(row.trip_count * scale) };
        })
      );
    }

    const params = new URLSearchParams(filters || {});
    return fetch(BASE_URL + "/stats/hourly?" + params.toString()).then(
      function (res) {
        if (!res.ok) throw new Error("Failed to fetch hourly stats");
        return res.json();
      }
    );
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

    const params = new URLSearchParams(filters || {});
    return fetch(BASE_URL + "/zones/top?" + params.toString()).then(
      function (res) {
        if (!res.ok) throw new Error("Failed to fetch top zones");
        return res.json();
      }
    );
  }

  function fetchInsights(filters) {
    if (MOCK_MODE) {
      return Promise.resolve(MOCK_INSIGHTS);
    }

    const params = new URLSearchParams(filters || {});
    return fetch(BASE_URL + "/insights?" + params.toString()).then(function (res) {
      if (!res.ok) throw new Error("Failed to fetch insights");
      return res.json();
    });
  }

  return { fetchSummary, fetchHourly, fetchTopZones, fetchInsights };
})();
