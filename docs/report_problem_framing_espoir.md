# Problem Framing & Dataset Analysis

*Data layer — Espoir*

## The dataset and its context

The project is built on the New York City Taxi & Limousine Commission (TLC)
Yellow Taxi trip records for January 2019. The raw file
(`yellow_tripdata_2019-01.csv`) holds **7,667,792 trips** across 18 columns:
identifiers (vendor, rate code, payment type), pickup and dropoff timestamps,
pickup and dropoff location zone IDs, passenger count, trip distance, and an
itemized fare breakdown (base fare, extra, tax, tip, tolls, surcharges, and
total). Location is encoded as a `LocationID` that maps, via the TLC zone
lookup table and the accompanying `taxi_zones` shapefile, to a borough, a named
zone, and a geographic polygon. The downstream system stores this in a
normalized relational database, serves it through an API, and presents it in a
dashboard, so the data layer's job is to turn the raw dump into a clean,
well-typed, analysis-ready table with a stable schema.

## Data challenges

Several issues had to be resolved before the data could be trusted:

- **Structural missingness.** `congestion_surcharge` is blank for
  **4,855,978 rows (about 63%)** — the surcharge had not been broadly applied
  yet in January 2019 — so its absence is structural rather than an error.
- **Invalid measurements.** A meaningful number of trips record zero or
  negative trip duration, non-positive distance, negative fares, or passenger
  counts of zero or above a normal cab's capacity.
- **Physically impossible trips.** Some records imply average speeds far beyond
  anything achievable on city streets, pointing to bad distance or timestamp
  values rather than real journeys.
- **Mislabelled time range.** Although the file is labelled "2019-01", a small
  number of pickups fall outside January 2019 (discussed at the end).
- **Geometry quirks.** Two zones (`LocationID` 56 and 103) are stored as
  multiple polygon features, which has to be handled so each zone resolves to a
  single centroid.

## Cleaning decisions and their effect

Every row removed is attributed to an explicit rule and counted in
`data/exclusion_log.csv`. The policy and its impact:

**Missing values (no rows dropped for these):**
- `passenger_count`: drop nulls (none were present in this file; the policy
  stands for robustness). Imputing a rider count would fabricate data.
- `RatecodeID`: relabel nulls to a documented "unknown" code (99) rather than
  drop (none were present).
- `congestion_surcharge`: fill the **4,855,978** blanks with `0.0`, reflecting
  that the charge did not broadly apply. This is a fill, not a removal.

**Removals (per-rule counts):**

| Rule | Records removed |
|---|---|
| Non-positive duration (dropoff ≤ pickup) | 6,294 |
| Non-positive distance (≤ 0 miles) | 48,801 |
| Extreme distance (> 100 miles) | 32 |
| Negative fare or total | 5,698 |
| Implausible passenger count (outside 1–6) | 115,626 |
| Implausible speed (> 100 mph) | 5,236 |
| Pickup outside January 2019 | 508 |
| Exact duplicate trips | 0 |
| **Total removed** | **182,195** |

Of the **7,667,792** starting rows, **182,195 were removed (2.38%)**, leaving
**7,485,597** clean trips. The dominant rule by far is implausible passenger
count (115,626 rows, almost two-thirds of all removals), driven mostly by trips
recording zero passengers. Thresholds were chosen to be conservative and
defensible: 1–6 passengers (a standard yellow cab's capacity), distances above
100 miles treated as errors and removed rather than capped (a capped value
would be invented), and a 100 mph ceiling on implied average speed. No exact
duplicate rows were found.

## Derived features

Eight features were engineered from the cleaned data, each guarded against
division by zero:

- **`trip_duration_min`** — dropoff minus pickup, in minutes. The most basic
  measure of a trip and a building block for speed.
- **`avg_speed_mph`** — distance divided by duration in hours; a congestion and
  data-sanity signal (the median is **10.12 mph**, consistent with dense city
  driving).
- **`fare_per_mile`** — fare divided by distance; normalizes cost for comparison
  across trips of different lengths.
- **`tip_pct`** — tip divided by fare, **computed for card trips only**. The TLC
  does not record cash tips, so including cash trips would understate tipping;
  restricting to card payments keeps the ratio meaningful.
- **`is_cross_borough`** — true when pickup and dropoff boroughs differ and both
  are known. **10.71%** of trips cross a borough boundary (801,721 trips), so
  most journeys stay within one borough.
- **`pickup_hour`**, **`pickup_day_of_week`**, **`time_of_day`** — calendar
  features (hour 0–23; day 0=Mon–6=Sun; and a morning/afternoon/evening/night
  bucket) that support temporal demand analysis on the dashboard.

For context, the median trip lasts **10.22 minutes**.

## One unexpected observation

The file is labelled January 2019, but its timestamps are not confined to that
month. In the raw data, **537 trips have a pickup outside January 2019**, and
the pickup timestamps span from **2001-02-02 all the way to 2088-01-24** — including
a handful of impossible future dates. The largest out-of-range group is
**December 2018, with 355 trips (about 66% of the out-of-window records)**:
late-December rides whose meters or records rolled into the January file. The
remainder is a thin scatter across 2018-11, 2009, 2008, and a few stray years.
The cleaning pipeline's January-window rule removed **508** such records (a few
of the 537 had already been dropped by earlier rules for other defects). The
practical lesson is that a monthly TLC file cannot be assumed to contain only
that month's trips; the pickup timestamp must be validated against the intended
window, not trusted from the filename.
