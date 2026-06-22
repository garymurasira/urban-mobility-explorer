# Urban Mobility Explorer

An interactive dashboard exploring NYC Yellow Taxi trip data (January 2019) —
cleaned and normalized into a database, served through a REST API, and
visualized in a filterable, map-driven frontend.

Team: Gary (Lead) · Espoir · David · Merci

## Prerequisites

- Python 3.x (data pipeline, backend)
- A modern browser (frontend)

## Setup

### 1. Data pipeline (Espoir)

> TODO (Espoir): commands to run the cleaning/feature pipeline in `data/src/`.

### 2. Database (Gary)

> TODO (Gary): how to build/load `database/schema.sql` into SQLite.

### 3. Backend API (David)

> TODO (David): how to install dependencies and run the Flask app in `backend/`.

### 4. Frontend (Merci)

No build step or install required — it's static HTML/CSS/JS.

1. Open `frontend/index.html` directly in a browser, **or** serve it locally
   (recommended, avoids any browser file:// restrictions):
   ```bash
   cd frontend
   python3 -m http.server 8000
   ```
   Then visit `http://localhost:8000`.
2. The dashboard calls the live backend directly (see `frontend/js/api.js`).
   It expects the Flask API at `BASE_URL` (`http://localhost:5000/api` by
   default) — update that constant if the backend runs elsewhere. With no
   backend reachable, each section will show its "Could not load…" error
   state rather than silently showing stale/fake numbers.
3. Requires internet access on first load for the Google Fonts, Chart.js,
   and Leaflet CDN assets (and Leaflet's map tiles). If those CDNs are
   unreachable, the page still renders with system-font fallbacks; only
   the Zones bar chart and the pickup density map will be missing (the
   Trends heatmap is plain CSS/JS and still works offline).

**Dashboard sections:**
- **Overview** — filter bar (date range, borough, payment type) + KPI cards
- **Trends** — trip demand heatmap (hour of day × day of week)
- **Zones** — pickup density map, top-zones chart, sortable zone table
- **Insights** — 3 data-backed insights plus a "why this matters" callout
  tying the findings to real urban-mobility/policy questions

### Deploying the frontend (optional bonus)

A `netlify.toml` is already in the repo root, configured to publish the
`frontend/` folder as a static site with no build step. To go live:

1. Go to [app.netlify.com](https://app.netlify.com) and sign in (free tier
   is enough).
2. "Add new site" → "Import an existing project" → connect this GitHub repo.
3. Netlify reads `netlify.toml` automatically — base directory `frontend`,
   no build command, publish directory `frontend`. Just click "Deploy".
4. Add the live URL to this README once it's up.

> Live URL: TODO

## Documentation

- `docs/architecture-diagram.png` — system architecture diagram (Gary)
- `docs/report_problem_framing_espoir.md` — dataset analysis, cleaning
  decisions, exclusion log summary (Espoir)
- `docs/report_insights_interpretation_merci.md` — the 3 data-backed
  insights shown on the dashboard, with derivation and real-world
  interpretation (Merci)
- `docs/ai-usage-log.md` — per-person record of AI tool usage during the
  project, required for the Individual Effort Verification multiplier

> TODO (Gary/David): add architecture/database design writeup and
> algorithm/complexity writeup sections once drafted, and assemble the
> full 2-3 page PDF report from all four sections.

## Video walkthrough

> TODO: add the link once recorded.
