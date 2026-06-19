"""Stage 4 — Features + schema normalization.

Two responsibilities:

1. ``add_features`` derives the engineered columns from the data contract
   (CLAUDE.md §4). Every division is guarded so a zero/NaN denominator yields
   ``NaN`` rather than ``inf``.
2. ``normalize_schema`` renames the raw TLC columns to the agreed snake_case
   contract, enforces final dtypes, and returns exactly the §4 columns in order.

Input:  cleaned trips DataFrame (raw TLC column names + integrate helpers).
Output: contract-shaped DataFrame ready for the database load.
"""

import numpy as np
import pandas as pd

# Raw TLC datetime columns (renamed in normalize_schema).
PICKUP_COL = "tpep_pickup_datetime"
DROPOFF_COL = "tpep_dropoff_datetime"

# Card payment_type code — tip_pct is only meaningful for card trips because
# TLC does not record cash tips (see add_features).
CARD_PAYMENT_TYPE = 1


def add_features(df):
    """Compute the derived feature columns required by the §4 contract.

    Divisions are guarded: any zero/NaN denominator produces NaN, never inf.
    """
    df = df.copy()

    # Trip duration in minutes. Cleaning guarantees dropoff > pickup, so this is
    # always positive; computed as a float.
    duration = df[DROPOFF_COL] - df[PICKUP_COL]
    duration_min = duration.dt.total_seconds() / 60.0
    df["trip_duration_min"] = duration_min.astype("float64")

    # Average speed (mph) = distance / duration_hours. NaN where duration is 0
    # (guarded with .where) so no inf is produced.
    duration_hours = duration_min / 60.0
    df["avg_speed_mph"] = (df["trip_distance"] / duration_hours).where(
        duration_hours > 0
    )

    return df
