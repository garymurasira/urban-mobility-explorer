"""Stage 3 — Clean.

Apply explicit, defensible data-integrity rules to the integrated trips frame
(still using raw TLC column names) and attribute **every removed row to a rule**
so a transparent exclusion log can be produced.

Design: each step is a small function that takes the frame plus a running list
of log records, performs one rule, and appends ``{rule, reason, rows_removed}``.
``clean_trips`` runs the steps in order and returns the cleaned frame alongside
the assembled exclusion log. Every threshold is a named constant below so the
policy is easy to read and justify in the report.

Input:  integrated trips DataFrame (raw TLC column names).
Output: (clean_df, exclusion_log_df).
"""

import numpy as np
import pandas as pd

# --- Missing-value policy ---------------------------------------------------
# passenger_count nulls are few; dropping is cleaner than inventing a count.
DROP_NULL_PASSENGER_COUNT = True
# RatecodeID nulls are relabelled to a documented "unknown" code, not dropped.
RATECODE_UNKNOWN_CODE = 99
# congestion_surcharge is mostly blank in Jan 2019 (it had not broadly applied);
# treat blanks as 0.0 rather than missing. This is a fill, not a removal.
CONGESTION_SURCHARGE_FILL = 0.0

# --- Outlier / validity thresholds ------------------------------------------
PASSENGER_COUNT_MIN = 1            # 0 passengers is treated as invalid.
PASSENGER_COUNT_MAX = 6            # standard yellow-cab seating cap.
MAX_TRIP_DISTANCE_MILES = 100.0    # beyond this is implausible for a city trip.
MAX_AVG_SPEED_MPH = 100.0          # faster than this implies bad time/distance.

# January 2019 window, half-open: [2019-01-01, 2019-02-01).
JANUARY_2019_START = pd.Timestamp("2019-01-01")
FEBRUARY_2019_START = pd.Timestamp("2019-02-01")

# Raw TLC column names used at this stage (renamed later in normalization).
PICKUP_COL = "tpep_pickup_datetime"
DROPOFF_COL = "tpep_dropoff_datetime"


def _record(log, rule, reason, before, after):
    """Append one exclusion-log entry, counting rows removed as before - after."""
    log.append({"rule": rule, "reason": reason, "rows_removed": int(before - after)})


def handle_missing_values(df, log):
    """Resolve missing values for passenger_count, RatecodeID, congestion_surcharge.

    - passenger_count: drop null rows (policy ``DROP_NULL_PASSENGER_COUNT``);
      they are few and imputing a rider count would be fabricated data.
    - RatecodeID: relabel nulls to ``RATECODE_UNKNOWN_CODE`` (kept, not dropped).
    - congestion_surcharge: fill nulls with ``CONGESTION_SURCHARGE_FILL`` (0.0);
      the surcharge had not broadly applied in Jan 2019. Fill, not a removal.
    """
    # 1. passenger_count missing -> drop.
    before = len(df)
    if DROP_NULL_PASSENGER_COUNT:
        df = df[df["passenger_count"].notna()]
    _record(log, "missing_passenger_count",
            "passenger_count was null; dropped (imputing a rider count is not defensible)",
            before, len(df))

    # 2. RatecodeID missing -> set to unknown code (no rows removed).
    ratecode_filled = int(df["RatecodeID"].isna().sum())
    df = df.copy()
    df["RatecodeID"] = df["RatecodeID"].fillna(RATECODE_UNKNOWN_CODE)
    _record(log, "missing_ratecode",
            f"RatecodeID null relabelled to {RATECODE_UNKNOWN_CODE} (unknown); "
            f"{ratecode_filled} values filled",
            len(df), len(df))

    # 3. congestion_surcharge missing -> fill 0.0 (no rows removed).
    congestion_filled = int(df["congestion_surcharge"].isna().sum())
    df["congestion_surcharge"] = df["congestion_surcharge"].fillna(CONGESTION_SURCHARGE_FILL)
    _record(log, "missing_congestion_surcharge",
            f"congestion_surcharge null filled with {CONGESTION_SURCHARGE_FILL} "
            f"(not broadly applied in Jan 2019); {congestion_filled} values filled",
            len(df), len(df))

    return df


def drop_duplicate_trips(df, log):
    """Drop exact duplicate trip rows (all columns identical)."""
    before = len(df)
    df = df.drop_duplicates()
    _record(log, "duplicate_trips",
            "exact duplicate rows (all columns identical) removed",
            before, len(df))
    return df


def remove_non_positive_duration(df, log):
    """Remove trips where dropoff is at or before pickup (zero/negative time)."""
    before = len(df)
    df = df[df[DROPOFF_COL] > df[PICKUP_COL]]
    _record(log, "non_positive_duration",
            "dropoff_datetime <= pickup_datetime (zero or negative trip time)",
            before, len(df))
    return df


def remove_invalid_distance(df, log):
    """Remove non-positive distances, then remove implausibly long trips.

    Extreme distances (> ``MAX_TRIP_DISTANCE_MILES``) are removed rather than
    capped: a capped value would be a fabricated distance, whereas removal keeps
    the surviving distances honest.
    """
    # trip_distance <= 0.
    before = len(df)
    df = df[df["trip_distance"] > 0]
    _record(log, "non_positive_distance",
            "trip_distance <= 0", before, len(df))

    # trip_distance > 100 miles (implausible for a city trip) -> remove.
    before = len(df)
    df = df[df["trip_distance"] <= MAX_TRIP_DISTANCE_MILES]
    _record(log, "extreme_distance",
            f"trip_distance > {MAX_TRIP_DISTANCE_MILES} miles (removed, not capped)",
            before, len(df))
    return df


def remove_negative_fare(df, log):
    """Remove trips with a negative fare_amount or total_amount."""
    before = len(df)
    df = df[(df["fare_amount"] >= 0) & (df["total_amount"] >= 0)]
    _record(log, "negative_fare",
            "fare_amount < 0 or total_amount < 0",
            before, len(df))
    return df


def filter_implausible_passenger_count(df, log):
    """Remove trips whose passenger_count is outside 1-6.

    0 is treated as invalid (a trip carries at least one rider); 7+ exceeds a
    standard yellow cab's seating capacity.
    """
    before = len(df)
    keep = (df["passenger_count"] >= PASSENGER_COUNT_MIN) & (
        df["passenger_count"] <= PASSENGER_COUNT_MAX
    )
    df = df[keep]
    _record(log, "implausible_passenger_count",
            f"passenger_count outside {PASSENGER_COUNT_MIN}-{PASSENGER_COUNT_MAX} "
            f"(0 treated as invalid)",
            before, len(df))
    return df


def filter_implausible_speed(df, log):
    """Remove trips whose implied average speed is non-finite or too high.

    Average speed = trip_distance / duration_hours. Duration is recomputed
    locally only for this filter (the real ``avg_speed_mph`` feature is produced
    later in features.py). Earlier steps guarantee positive duration and
    distance, so the divide is safe; the non-finite guard is belt-and-braces.
    """
    before = len(df)
    duration_hours = (df[DROPOFF_COL] - df[PICKUP_COL]).dt.total_seconds() / 3600.0
    avg_speed = df["trip_distance"] / duration_hours
    keep = np.isfinite(avg_speed) & (avg_speed <= MAX_AVG_SPEED_MPH)
    df = df[keep]
    _record(log, "implausible_speed",
            f"implied avg speed > {MAX_AVG_SPEED_MPH} mph or non-finite",
            before, len(df))
    return df


def drop_outside_january_2019(df, log):
    """Remove trips whose pickup falls outside January 2019.

    The file carries stragglers from other periods (2018 — and even older
    stray timestamps). Keep only the half-open window
    [2019-01-01, 2019-02-01).
    """
    before = len(df)
    keep = (df[PICKUP_COL] >= JANUARY_2019_START) & (df[PICKUP_COL] < FEBRUARY_2019_START)
    df = df[keep]
    _record(log, "pickup_outside_january_2019",
            "pickup_datetime outside [2019-01-01, 2019-02-01)",
            before, len(df))
    return df


def clean_trips(df):
    """Run all integrity rules in order; return (clean_df, exclusion_log_df)."""
    df = df.copy()
    log = []

    df = handle_missing_values(df, log)
    df = drop_duplicate_trips(df, log)
    df = remove_non_positive_duration(df, log)
    df = remove_invalid_distance(df, log)
    df = remove_negative_fare(df, log)
    df = filter_implausible_passenger_count(df, log)
    df = filter_implausible_speed(df, log)
    df = drop_outside_january_2019(df, log)

    return df, pd.DataFrame(log)
