# Stage 3: integrity rules; every removed row is attributed to a named rule.

import numpy as np
import pandas as pd

# Missing-value policy
DROP_NULL_PASSENGER_COUNT = True
RATECODE_UNKNOWN_CODE = 99
CONGESTION_SURCHARGE_FILL = 0.0

# Outlier / validity thresholds
PASSENGER_COUNT_MIN = 1
PASSENGER_COUNT_MAX = 6
MAX_TRIP_DISTANCE_MILES = 100.0
MAX_AVG_SPEED_MPH = 100.0

JANUARY_2019_START = pd.Timestamp("2019-01-01")
FEBRUARY_2019_START = pd.Timestamp("2019-02-01")

PICKUP_COL = "tpep_pickup_datetime"
DROPOFF_COL = "tpep_dropoff_datetime"


def _record(log, rule, reason, before, after):
    log.append({"rule": rule, "reason": reason, "rows_removed": int(before - after)})


def handle_missing_values(df, log):
    # passenger_count null -> drop; ratecode null -> 99; congestion null -> 0.0.
    before = len(df)
    if DROP_NULL_PASSENGER_COUNT:
        df = df[df["passenger_count"].notna()]
    _record(log, "missing_passenger_count",
            "passenger_count was null; dropped (imputing a rider count is not defensible)",
            before, len(df))

    ratecode_filled = int(df["RatecodeID"].isna().sum())
    df = df.copy()
    df["RatecodeID"] = df["RatecodeID"].fillna(RATECODE_UNKNOWN_CODE)
    _record(log, "missing_ratecode",
            f"RatecodeID null relabelled to {RATECODE_UNKNOWN_CODE} (unknown); "
            f"{ratecode_filled} values filled",
            len(df), len(df))

    congestion_filled = int(df["congestion_surcharge"].isna().sum())
    df["congestion_surcharge"] = df["congestion_surcharge"].fillna(CONGESTION_SURCHARGE_FILL)
    _record(log, "missing_congestion_surcharge",
            f"congestion_surcharge null filled with {CONGESTION_SURCHARGE_FILL} "
            f"(not broadly applied in Jan 2019); {congestion_filled} values filled",
            len(df), len(df))

    return df


def drop_duplicate_trips(df, log):
    before = len(df)
    df = df.drop_duplicates()
    _record(log, "duplicate_trips",
            "exact duplicate rows (all columns identical) removed",
            before, len(df))
    return df


def remove_non_positive_duration(df, log):
    before = len(df)
    df = df[df[DROPOFF_COL] > df[PICKUP_COL]]
    _record(log, "non_positive_duration",
            "dropoff_datetime <= pickup_datetime (zero or negative trip time)",
            before, len(df))
    return df


def remove_invalid_distance(df, log):
    # remove non-positive, then extreme (>100mi) distances.
    before = len(df)
    df = df[df["trip_distance"] > 0]
    _record(log, "non_positive_distance",
            "trip_distance <= 0", before, len(df))

    before = len(df)
    df = df[df["trip_distance"] <= MAX_TRIP_DISTANCE_MILES]
    _record(log, "extreme_distance",
            f"trip_distance > {MAX_TRIP_DISTANCE_MILES} miles (removed, not capped)",
            before, len(df))
    return df


def remove_negative_fare(df, log):
    before = len(df)
    df = df[(df["fare_amount"] >= 0) & (df["total_amount"] >= 0)]
    _record(log, "negative_fare",
            "fare_amount < 0 or total_amount < 0",
            before, len(df))
    return df


def filter_implausible_passenger_count(df, log):
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
    # duration recomputed locally just for this filter.
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
    before = len(df)
    keep = (df[PICKUP_COL] >= JANUARY_2019_START) & (df[PICKUP_COL] < FEBRUARY_2019_START)
    df = df[keep]
    _record(log, "pickup_outside_january_2019",
            "pickup_datetime outside [2019-01-01, 2019-02-01)",
            before, len(df))
    return df


def build_exclusion_log(records):
    # per-rule records -> DataFrame + TOTAL row.
    log_df = pd.DataFrame(records, columns=["rule", "reason", "rows_removed"])
    total = pd.DataFrame(
        [{
            "rule": "TOTAL",
            "reason": "all rules combined",
            "rows_removed": int(log_df["rows_removed"].sum()),
        }]
    )
    return pd.concat([log_df, total], ignore_index=True)


def clean_trips(df):
    # run all rules in order; return (clean_df, exclusion_log_df).
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

    clean_df = df.reset_index(drop=True)
    return clean_df, build_exclusion_log(log)
