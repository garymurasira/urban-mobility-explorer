# Data Layer — Cleaning Pipeline

> **Work in progress.** The pipeline is currently scaffolded with stage stubs;
> stage logic is not implemented yet.

Cleans the raw **NYC Yellow Taxi Trip** data (January 2019) and produces a
normalized, feature-enriched dataset for the database load.

## Stages

The pipeline runs five stages in order:

1. **load** (`load.py`) — read the raw trips CSV with explicit dtypes and
   parsed datetimes.
2. **integrate** (`integrate.py`) — join `taxi_zone_lookup.csv` for pickup /
   dropoff borough + zone, and derive zone centroids from the `taxi_zones`
   shapefile.
3. **clean** (`clean.py`) — handle missing values, drop duplicates, remove
   outliers/invalid rows, and log every exclusion.
4. **features** (`features.py`) — derive engineered columns (trip duration,
   average speed, fare per mile, tip %, cross-borough flag, time buckets).
5. **export** — write the cleaned dataset and a ~1,000-row sample.

## How to run

From the repository root:

```bash
pip install -r data/requirements.txt
python -m data.src.pipeline
```

## Inputs and outputs

| Path | Purpose | Tracked in Git? |
|---|---|---|
| `data/raw/` | raw CSV + `taxi_zone_lookup.csv` + `taxi_zones` shapefile | No (git-ignored) |
| `data/processed/` | full cleaned output | No (git-ignored) |
| `data/sample/` | ~1,000-row cleaned sample for the DB load | Yes |
| `data/exclusion_log.csv` | per-rule removal counts | Yes |
