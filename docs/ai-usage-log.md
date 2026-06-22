# AI Usage Log

Each person records what they used AI assistance for and how they verified
or changed the output, per the project brief's Individual Effort
Verification requirement.

---

## Merci (Frontend)

**What I used AI for:**
- Researching how to implement Chart.js (bar charts for the zones
  comparison, configuring scales/legends) and Leaflet (map initialization,
  markers, popups) since I hadn't used either library before.
- Researching approaches for more complex JavaScript concepts I wasn't
  confident with yet — e.g. how an event-driven filter pattern (a single
  custom event that multiple sections can listen to independently) is
  typically structured, and how to shape a mock data layer so it mirrors
  a real API's expected response format.
- Getting debugging help to understand issues I couldn't diagnose on my
  own, including:
  - Why the Trends heatmap's day rows rendered misaligned on narrow
    screens — learned it was a CSS Grid auto-placement pitfall (mixing
    explicit `grid-row` placement with auto-placed items), which I didn't
    know about beforehand.
  - Why a real mobile screenshot showed an unexpected blue/orange color
    tint — learned it was the browser's forced-dark-mode color inversion
    rather than a CSS bug, and that declaring `color-scheme: light` was
    the standard fix.

**How I verified/changed the output:**
- Tested every change myself in an actual browser (including real mobile
  screenshots at narrow viewport widths) rather than assuming a suggested
  fix worked — the heatmap misalignment bug above was only caught this way.
- Manually computed WCAG contrast ratios for the yellow accent color used
  as text and confirmed it failed the 4.5:1 minimum before changing it,
  rather than taking a color suggestion at face value.
- Cross-checked all "insight" figures shown on the dashboard against the
  actual cleaned sample dataset (`data/sample/trips_clean_sample.csv`) and
  Espoir's cleaning report — caught and corrected an earlier set of
  placeholder numbers that turned out to be inconsistent with the real
  data (e.g. a "1.9M trips" figure that didn't match the actual 7,485,597
  cleaned count).

---

## David (Backend API & Algorithm)

---

## 1. Diagnosing the MySQL connection error

**What I asked AI:** Why is my Flask app throwing `InterfaceError: Can't connect to MySQL server`?

**What AI did:** Identified that the Aiven free-tier MySQL service was powered off due to storage limits, and that the `.env` file still had the old Aiven credentials pointing to a dead server.

**What I verified and changed:** I confirmed the Aiven dashboard showed the service as "Powered off". I then set up a local MySQL instance and updated both `.env` files (`database/.env` and `backend/.env`) manually with my local credentials.

---

## 2. Setting up local MySQL and loading the database

**What I asked AI:** How do I set up MySQL locally and load the data?

**What AI did:** Provided the sequence of commands to install MySQL via Homebrew, create the database, apply `schema.sql`, and run `load_data.py`.

**What I verified and changed:** I ran each command myself, confirmed MySQL started correctly, and verified the load script output showed `1000 rows loaded, 0 rows failed` before trusting the data was in the database.

---

## 3. Understanding the pipeline and data flow

**What I asked AI:** How does the pipeline connect to my API endpoints?

**What AI did:** Explained that `pipeline.py` produces `trips_clean_sample.csv` and `zones_reference.csv`, which `load_data.py` then inserts into MySQL, which my Flask API queries.

**What I verified and changed:** I traced the file paths in `load_data.py` myself to confirm they matched where the sample files were placed, and tested each endpoint in the browser to confirm real data was returned.

---

## 4. Git workflow and protecting credentials

**What I asked AI:** How do I push my changes to GitHub without committing the `.env` file?

**What I verified and changed:** I ran `cat .gitignore` myself to confirm `.env` and `**/.env` were already listed before pushing. I chose which files to stage based on what VS Code showed as modified (`M`), not blindly following AI suggestions.

---

*All AI suggestions were reviewed, tested, and verified before being trusted.*

---

> TODO (Gary, Espoir): add your own entries above, following the same
> format — what you used AI for, and how you verified or changed it.