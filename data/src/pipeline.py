# Pipeline: load -> integrate -> clean -> features -> normalize -> export.
# Run: python3 -m data.src.pipeline

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

PROCESSED_DIR = Path("data/processed")  # git-ignored
SAMPLE_DIR = Path("data/sample")
PROCESSED_PARQUET = PROCESSED_DIR / "trips_clean.parquet"
SAMPLE_CSV = SAMPLE_DIR / "trips_clean_sample.csv"
ZONES_REFERENCE_CSV = SAMPLE_DIR / "zones_reference.csv"
EXCLUSION_LOG_CSV = Path("data/exclusion_log.csv")

SAMPLE_SIZE = 1000
SAMPLE_SEED = 42

logger = logging.getLogger("pipeline")


def build_zones_reference():
    # zone names + centroids for Gary's zones dimension.
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
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out.to_parquet(PROCESSED_PARQUET, index=False)
    logger.info("wrote %s (%d rows)", PROCESSED_PARQUET, len(out))

    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    sample = out.sample(
        n=min(SAMPLE_SIZE, len(out)), random_state=SAMPLE_SEED
    ).sort_values("pickup_datetime")
    sample.to_csv(SAMPLE_CSV, index=False)
    logger.info("wrote %s (%d rows)", SAMPLE_CSV, len(sample))

    zones = build_zones_reference()
    zones.to_csv(ZONES_REFERENCE_CSV, index=False)
    logger.info("wrote %s (%d rows)", ZONES_REFERENCE_CSV, len(zones))

    log_df.to_csv(EXCLUSION_LOG_CSV, index=False)
    logger.info("wrote %s (%d rules)", EXCLUSION_LOG_CSV, len(log_df))


def run(path=RAW_PATH):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    start = time.perf_counter()

    trips = load_trips(path)
    logger.info("loaded %d raw rows from %s", len(trips), path)

    zones = load_zone_lookup()
    trips = attach_zones(trips, zones)
    logger.info("integrated zone lookup -> %d rows", len(trips))

    trips, log_df = clean_trips(trips)
    logger.info("cleaned -> %d rows (%d removed)",
                len(trips), int(log_df.loc[log_df["rule"] == "TOTAL", "rows_removed"].iloc[0]))

    trips = add_features(trips)
    logger.info("added derived features -> %d columns", trips.shape[1])

    out = normalize_schema(trips)
    logger.info("normalized to contract schema -> %d columns", out.shape[1])

    export_outputs(out, log_df)

    logger.info("pipeline complete: %d clean rows in %.1fs",
                len(out), time.perf_counter() - start)
    return out


if __name__ == "__main__":
    run()
