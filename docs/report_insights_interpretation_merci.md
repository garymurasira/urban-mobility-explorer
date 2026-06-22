# Insights & Interpretation

*Frontend & Insights — Merci*

## Note on data source

The live backend/database connection between the dashboard and the full
7,485,597-row cleaned dataset was still being finalized with David at the
time of writing. The figures below are computed directly from
`data/sample/trips_clean_sample.csv` (a 1,000-row cleaned sample produced by
Espoir's pipeline) joined against `data/sample/zones_reference.csv`, and are
cross-checked against the full-dataset figures already reported in
`docs/report_problem_framing_espoir.md` where available (e.g. the
cross-borough rate). They are directional, not final — the dashboard is
wired to re-derive them from the live API the moment it's connected (see
`frontend/js/api.js`, `MOCK_MODE`).

## Insight 1 — Manhattan dominates pickup demand

**90.5%** of sampled pickups originate in Manhattan, compared to 6.2% in
Queens and just over 1% in Brooklyn. The Zones map and the "Top zones by
trip count" chart back this up directly — of the busiest individual pickup
zones, Midtown Center, Times Sq/Theatre District, and the Upper East Side
all rank near the top, all in Manhattan.

**What it means:** taxi demand isn't evenly distributed across the city's
geography — it's concentrated in a small footprint of central Manhattan.
For city planning or fleet allocation, this suggests that supply-side
decisions (where to position available cabs, where congestion pricing or
curb management matters most) should weight Manhattan far more heavily than
its share of the city's land area or even its population would suggest.

## Insight 2 — Most trips stay within one borough

Only **11.8%** of sampled trips cross a borough line (the full-dataset
figure, from Espoir's cleaning report, is **10.71%** — consistent with the
sample). The remaining ~89% start and end in the same borough.

**What it means:** despite popular narratives about commuting "into the
city," the large majority of yellow-taxi demand is short, local movement —
not cross-borough travel. This matters for interpreting every other chart
on the dashboard: most of what's being measured is intra-Manhattan (or
intra-whatever-borough) movement, not bridge-and-tunnel commuting.

## Insight 3 — Night trips cost more than any other time of day

Trips between midnight and 6am average **$14.75**, versus **$11.96** for the
rest of the day combined — about **23% higher**. This isn't simply "less
traffic, but somehow pricier" — it lines up with the NYC TLC's overnight
surcharge, a mandated $0.50 (now higher) addition to every fare between
8pm and 6am, plus likely longer average trip distances overnight (e.g.
airport runs, bar-to-home trips) that the fare-per-mile structure would
also capture.

**What it means:** time-of-day isn't just a demand signal (see the Trends
heatmap) — it's a pricing signal too. Any cost-of-mobility narrative for the
city needs to account for *when* people travel, not just *how far*.

## Visuals backing these insights

- Insight 1 → Zones section: pickup density map + "Top 7 zones by trip
  count" bar chart.
- Insight 2 → Overview KPI card ("Cross-borough trips") + the same figure
  surfaced as an Insight card.
- Insight 3 → Trends section: the hour x day-of-week heatmap shows *when*
  trips happen; this insight explains *why* the cost differs across those
  same hours.
