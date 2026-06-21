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
2. The dashboard currently runs against **mock data** (see
   `frontend/js/api.js`, `MOCK_MODE`). Once the backend is running, set
   `MOCK_MODE = false` and point `BASE_URL` at the live API to switch to
   real data — no other frontend files need to change.
3. Requires internet access on first load for the Google Fonts, Chart.js,
   and Leaflet CDN assets (and Leaflet's map tiles). If those CDNs are
   unreachable, the page still renders with system-font fallbacks; only
   the hourly chart and the zone map will be missing.

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

## Video walkthrough

> TODO: add the link once recorded.
