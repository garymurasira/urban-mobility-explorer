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


def clean_trips(df):
    """Run all integrity rules in order; return (clean_df, exclusion_log_df)."""
    df = df.copy()
    log = []

    df = handle_missing_values(df, log)
    df = drop_duplicate_trips(df, log)

    return df, pd.DataFrame(log)
