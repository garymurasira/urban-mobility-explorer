"""Pipeline orchestrator.

Runs the data layer end to end:
    load -> integrate -> clean -> features -> normalize -> export

Run from the repo root with:
    python3 -m data.src.pipeline

Raw input lives in data/raw/ (git-ignored). Outputs:
- data/processed/trips_clean.parquet  full cleaned dataset (git-ignored)
- data/sample/trips_clean_sample.csv  1,000-row sample for Gary (committed)
- data/sample/zones_reference.csv     zone names + centroids for Gary (committed)
- data/exclusion_log.csv              per-rule removal counts (committed)

The pipeline does a single full-file pass: 7.67M rows fit comfortably in memory
on a typical workstation, which keeps the exclusion-log counts and the exact
duplicate detection simple and correct. (If the file ever outgrows memory, the
fallback is chunked reading via load_trips(chunksize=...); note that exact
cross-chunk duplicate detection would then require a global key/hash pass.)
"""

import logging
import time
from pathlib import Path

from data.src.load import load_trips, RAW_PATH
from data.src.integrate import (
    load_zone_lookup,
    load_zone_centroids,
    attach_zones,
)
from data.src.clean import clean_trips
from data.src.features import add_features, normalize_schema

# --- Output locations -------------------------------------------------------
PROCESSED_DIR = Path("data/processed")          # git-ignored
SAMPLE_DIR = Path("data/sample")                # committed deliverables
PROCESSED_PARQUET = PROCESSED_DIR / "trips_clean.parquet"
SAMPLE_CSV = SAMPLE_DIR / "trips_clean_sample.csv"
ZONES_REFERENCE_CSV = SAMPLE_DIR / "zones_reference.csv"
EXCLUSION_LOG_CSV = Path("data/exclusion_log.csv")

# 1,000-row reproducible sample for Gary's first DB load.
SAMPLE_SIZE = 1000
SAMPLE_SEED = 42

logger = logging.getLogger("pipeline")


def build_zones_reference():
    """Zone names + centroids for Gary's zones dimension.

    Columns: location_id, borough, zone, service_zone, centroid_lat,
    centroid_lon. Left-joined from the lookup so every zone id is present;
    centroids are null for the few ids without a shapefile polygon.
    """
    lookup = load_zone_lookup().rename(
        columns={"LocationID": "location_id", "Borough": "borough", "Zone": "zone"}
    )
    centroids = load_zone_centroids()
    ref = lookup.merge(centroids, on="location_id", how="left")
    return ref[
        ["location_id", "borough", "zone", "service_zone",
         "centroid_lat", "centroid_lon"]
    ]


def export_outputs(out, log_df):
    """Write all pipeline outputs to disk and log where each landed."""
    # Full cleaned dataset -> parquet (git-ignored, never committed).
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out.to_parquet(PROCESSED_PARQUET, index=False)
    logger.info("wrote %s (%d rows)", PROCESSED_PARQUET, len(out))

    # 1,000-row reproducible sample for Gary (committed).
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    sample = out.sample(
        n=min(SAMPLE_SIZE, len(out)), random_state=SAMPLE_SEED
    ).sort_values("pickup_datetime")
    sample.to_csv(SAMPLE_CSV, index=False)
    logger.info("wrote %s (%d rows)", SAMPLE_CSV, len(sample))

    # Zones reference (names + centroids) for Gary's zones dimension (committed).
    zones = build_zones_reference()
    zones.to_csv(ZONES_REFERENCE_CSV, index=False)
    logger.info("wrote %s (%d rows)", ZONES_REFERENCE_CSV, len(zones))

    # Per-rule exclusion log (committed, graded deliverable).
    log_df.to_csv(EXCLUSION_LOG_CSV, index=False)
    logger.info("wrote %s (%d rules)", EXCLUSION_LOG_CSV, len(log_df))


def run(path=RAW_PATH):
    """Execute the full pipeline and write outputs. Returns the cleaned frame."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    start = time.perf_counter()

    # 1. load
    trips = load_trips(path)
    logger.info("loaded %d raw rows from %s", len(trips), path)

    # 2. integrate (zone lookup join + borough/zone columns)
    zones = load_zone_lookup()
    trips = attach_zones(trips, zones)
    logger.info("integrated zone lookup -> %d rows", len(trips))

    # 3. clean (with exclusion log)
    trips, log_df = clean_trips(trips)
    logger.info("cleaned -> %d rows (%d removed)",
                len(trips), int(log_df.loc[log_df["rule"] == "TOTAL", "rows_removed"].iloc[0]))

    # 4. features
    trips = add_features(trips)
    logger.info("added derived features -> %d columns", trips.shape[1])

    # 5. normalize to the agreed §4 output schema
    out = normalize_schema(trips)
    logger.info("normalized to contract schema -> %d columns", out.shape[1])

    # 6. export
    export_outputs(out, log_df)

    logger.info("pipeline complete: %d clean rows in %.1fs",
                len(out), time.perf_counter() - start)
    return out


if __name__ == "__main__":
    run()
