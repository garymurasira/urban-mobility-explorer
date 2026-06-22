# Urban Mobility Explorer

An interactive dashboard exploring the **NYC Yellow Taxi Trip dataset (January 2019)**.
Raw trip records (~7.67M rows) are cleaned and feature-enriched by a Python pipeline,
loaded into a normalized relational database, served through a Flask REST API, and
visualized in a filterable, map-driven web dashboard with real urban-mobility insights.

**Team:** Gary (lead — architecture & database) · Espoir (data cleaning & features) ·
David (backend API & algorithm) · Merci (frontend dashboard & storytelling)

---

## Architecture

See the system diagram at [`docs/architecture-diagram.png`](docs/architecture-diagram.png).

Data flows in one direction through four layers:

```
raw TLC data  →  cleaning pipeline (data/)  →  database (MySQL)  →  REST API (backend/)  →  dashboard (frontend/)
```

Each layer depends on the one before it, so set them up in that order.

---

## Prerequisites

- **Python 3.10+** and `pip` (data pipeline, database loader, backend API)
- **MySQL 8.x** server running locally (the schema uses InnoDB; the loader and API
  connect with `mysql-connector-python`)
- A modern **web browser** (frontend)
- ~Several GB of free RAM and disk **only if** you re-run the full data pipeline on the
  raw 657 MB CSV. Loading the database from the committed sample needs neither.

---

## Setup & run

Run the layers in dependency order. All commands assume you start from the **repository root**
unless stated otherwise.

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/garymurasira/urban-mobility-explorer.git
cd urban-mobility-explorer

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
```

### 2. Data pipeline (`data/`)

> **Optional for graders.** The database loads from a committed 1,000-row sample
> (`data/sample/`), so you can skip straight to step 3. Run this step only to
> regenerate the full cleaned dataset from the raw file.

Install the data dependencies:

```bash
pip3 install -r data/requirements.txt
```

Download the raw inputs from the **NYC TLC Trip Record Data** page (Yellow Taxi,
January 2019) plus the zone lookup table and `taxi_zones` shapefile, and place them
(git-ignored, never committed) under `data/raw/`:

```
data/raw/
  yellow_tripdata_2019-01.csv     ~657 MB, ~7.67M rows
  taxi_zone_lookup.csv            LocationID -> borough / zone
  taxi_zones/                     taxi_zones.shp (+ .dbf/.prj/.shx/...)
```

Run the pipeline (load → integrate → clean → features → normalize → export):

```bash
python3 -m data.src.pipeline
```

Outputs:

| Path | What | Committed? |
|---|---|---|
| `data/processed/trips_clean.parquet` | full cleaned dataset | No (git-ignored) |
| `data/sample/trips_clean_sample.csv` | 1,000-row sample for the DB load | Yes |
| `data/sample/zones_reference.csv` | zone names + centroids for the zones table | Yes |
| `data/exclusion_log.csv` | per-rule removal counts | Yes |

See [`data/README.md`](data/README.md) for the cleaning rules and full run details.

### 3. Database (`database/` + MySQL)

The schema is **MySQL** (5 tables: `trips`, `zones`, `vendors`, `rate_codes`,
`payment_types`).

**a. Create the database** in your MySQL server:

```sql
CREATE DATABASE urban_mobility;
```

**b. Configure credentials.** The table creator (in `backend/`) and the data loader
(in `database/`) each read their own `.env` file. Copy both examples and fill in your
MySQL username/password:

```bash
cp backend/.env.example  backend/.env
cp database/.env.example database/.env
```

Set `DB_NAME=urban_mobility` (and `DB_HOST`, `DB_PORT=3306`, `DB_USER`, `DB_PASSWORD`)
in **both** files.

**c. Create the tables** from `database/schema.sql` using the helper script:

```bash
cd backend
python3 setup_db.py            # reads ../database/schema.sql, creates all tables
cd ..
```

> Alternatively, load the schema directly: `mysql -u <user> -p urban_mobility < database/schema.sql`

**d. Load the data** (dimension tables + the cleaned trips sample):

```bash
cd database
python3 load_data.py           # loads from data/sample/*.csv
cd ..
```

You should see per-table row counts ending in `Done.`

### 4. Backend API (`backend/`)

Install backend dependencies (uses `backend/.env` from step 3b):

```bash
pip3 install -r backend/requirements.txt
```

Start the Flask app from inside `backend/` (its imports expect that working directory):

```bash
cd backend
python3 app.py                 # serves on http://localhost:5000
```

The API base URL is **`http://localhost:5000/api`**. Key endpoints:

| Method & path | Purpose |
|---|---|
| `GET /api/health` | Health check — confirms the API is up and can reach the database |
| `GET /api/stats/summary` | Headline KPIs (total trips, avg fare/distance/duration, % cross-borough); supports `date_from`, `date_to`, `borough` filters |
| `GET /api/stats/hourly` | Trip counts per (day-of-week × hour) for the Trends heatmap |
| `GET /api/zones/top` | Top pickup zones by trip count |
| `GET /api/insights` | Aggregates behind the Insights cards (peak hour, cross-borough share, tips by payment type) |
| `GET /api/trips` | Paginated, sortable raw trip rows |

Quick check: `curl http://localhost:5000/api/health` should return `{"status": "ok", ...}`.

### 5. Frontend (`frontend/`)

The dashboard is static HTML/CSS/JS — no build step. Serve it locally (recommended over
opening the file directly, to avoid `file://` restrictions):

```bash
cd frontend
python3 -m http.server 8000
```

Then visit **`http://localhost:8000`**.

The dashboard calls the backend directly. The API base URL is set in
[`frontend/js/api.js`](frontend/js/api.js) as:

```js
const BASE_URL = "http://localhost:5000/api";
```

Update that constant if the backend runs elsewhere. With no backend reachable, each
section shows its "could not load" error state rather than fake numbers. First load needs
internet access for the Google Fonts, Chart.js, and Leaflet CDN assets (the page still
renders with fallbacks if those are unreachable).

**Dashboard sections:** Overview (filters + KPI cards) · Trends (demand heatmap) ·
Zones (pickup map, top-zones chart, zone table) · Insights (data-backed findings).

---

## Deployment (optional bonus)

**The app is deployed and live** — all three layers are hosted separately:

| Layer | Host | Notes |
|---|---|---|
| Database | [FreeSQLDatabase](https://www.freesqldatabase.com/) | Free hosted MySQL; same schema as local, loaded via `database/load_data.py` |
| Backend API | [Render](https://render.com) | Deployed via [`backend/Procfile`](backend/Procfile) (`web: gunicorn app:app`); `DB_*` env vars point at the FreeSQLDatabase instance above |
| Frontend | [Vercel](https://vercel.com) | Static deploy of `frontend/`, Root Directory set to `frontend`, no build step |

`frontend/js/api.js`'s `BASE_URL` is already pointed at the live Render backend, so the
deployed frontend talks to the deployed backend/database with no local setup needed.

> **Live URLs:**
> - Backend API: https://urban-mobility-explorer.onrender.com
> - Frontend dashboard: https://urban-mobility-explorer.vercel.app/

---

## Documentation

Available in [`docs/`](docs/):

- [`docs/architecture-diagram.png`](docs/architecture-diagram.png) — system architecture diagram
- [`docs/report_problem_framing_espoir.md`](docs/report_problem_framing_espoir.md) — dataset
  analysis, cleaning decisions, and exclusion-log summary
- [`docs/report_insights_interpretation_merci.md`](docs/report_insights_interpretation_merci.md) —
  the 3 data-backed insights shown on the dashboard, with derivation and real-world interpretation
- [`docs/ai-usage-log.md`](docs/ai-usage-log.md) — per-person record of AI tool usage, required
  for the Individual Effort Verification multiplier

### Pending before submission (not yet in the repo)

- **Assembled PDF report** — the full 2–3 page report combining all team sections (architecture
  & design writeup, algorithm/complexity writeup, plus the two sections above)

---

## Video walkthrough

> **REQUIRED before submission — placeholder.** A screen-recorded walkthrough of the running
> system must be linked here. (Cannot be generated automatically.)
>
> Video link: https://youtu.be/_DjAD7yMSrM?si=6R3KwN8UC0CjrY2u

---

## Team & roles

| Member | Role | Area |
|---|---|---|
| **Gary** | Lead | Architecture & database (`database/`) |
| **Espoir** | Data | Cleaning pipeline, integrity & features (`data/`) |
| **David** | Backend | Flask REST API & custom algorithm (`backend/`) |
| **Merci** | Frontend | Dashboard & storytelling (`frontend/`) |
</content>
</invoke>
