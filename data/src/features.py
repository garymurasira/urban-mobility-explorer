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

# time_of_day buckets by pickup hour (inclusive ranges). Hours not covered by
# morning/afternoon/evening fall to night, i.e. 00-05 and 22-23.
MORNING_HOURS = range(6, 12)     # 06:00-11:59
AFTERNOON_HOURS = range(12, 17)  # 12:00-16:59
EVENING_HOURS = range(17, 22)    # 17:00-21:59
# NIGHT = remaining hours (22-23 and 00-05).


def _time_of_day(hour):
    """Map an array of pickup hours (0-23) to morning/afternoon/evening/night."""
    conditions = [
        hour.isin(list(MORNING_HOURS)),
        hour.isin(list(AFTERNOON_HOURS)),
        hour.isin(list(EVENING_HOURS)),
    ]
    choices = ["morning", "afternoon", "evening"]
    return np.select(conditions, choices, default="night")


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

    # Fare per mile = fare_amount / trip_distance. NaN where distance is 0.
    df["fare_per_mile"] = (df["fare_amount"] / df["trip_distance"]).where(
        df["trip_distance"] > 0
    )

    # Tip percentage = tip_amount / fare_amount, card trips only. TLC does not
    # record cash tips, so for non-card trips tip_amount is structurally 0 and a
    # tip rate would be misleading — restrict to card and NaN everything else
    # (also NaN where fare_amount is 0 to guard the division).
    is_card = df["payment_type"] == CARD_PAYMENT_TYPE
    df["tip_pct"] = (df["tip_amount"] / df["fare_amount"]).where(
        is_card & (df["fare_amount"] > 0)
    )

    # Cross-borough flag: True only when both boroughs are known and differ.
    # Unknown zones (null borough from the integrate left-join) are treated as
    # not-confirmed-cross-borough (False) rather than inflating the rate.
    both_known = df["pu_borough"].notna() & df["do_borough"].notna()
    df["is_cross_borough"] = (df["pu_borough"] != df["do_borough"]) & both_known

    # Calendar features from the pickup timestamp.
    df["pickup_hour"] = df[PICKUP_COL].dt.hour                 # 0-23
    df["pickup_day_of_week"] = df[PICKUP_COL].dt.dayofweek     # 0=Mon .. 6=Sun
    df["time_of_day"] = _time_of_day(df["pickup_hour"])

    return df


# --- Schema contract (CLAUDE.md §4) -----------------------------------------
# Raw TLC name -> agreed snake_case contract name. Names already in contract
# form (e.g. trip_distance, the itemized fare columns) are intentionally absent.
RENAME_MAP = {
    "VendorID": "vendor_id",
    "tpep_pickup_datetime": "pickup_datetime",
    "tpep_dropoff_datetime": "dropoff_datetime",
    "RatecodeID": "rate_code_id",
    "PULocationID": "pu_location_id",
    "DOLocationID": "do_location_id",
}

# Final dtypes grouped by target type.
INT_COLUMNS = [
    "vendor_id", "passenger_count", "rate_code_id",
    "pu_location_id", "do_location_id", "payment_type",
    "pickup_hour", "pickup_day_of_week",
]
FLOAT_COLUMNS = [
    "trip_distance",
    "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount",
    "improvement_surcharge", "congestion_surcharge", "total_amount",
    "trip_duration_min", "avg_speed_mph", "fare_per_mile", "tip_pct",
]
STRING_COLUMNS = ["store_and_fwd_flag", "time_of_day"]
DATETIME_COLUMNS = ["pickup_datetime", "dropoff_datetime"]

# Exact contract output columns, in order.
CONTRACT_COLUMNS = [
    "vendor_id",
    "pickup_datetime",
    "dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "rate_code_id",
    "store_and_fwd_flag",
    "pu_location_id",
    "do_location_id",
    "payment_type",
    "fare_amount",
    "extra",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "congestion_surcharge",
    "total_amount",
    "trip_duration_min",
    "avg_speed_mph",
    "fare_per_mile",
    "tip_pct",
    "is_cross_borough",
    "pickup_hour",
    "pickup_day_of_week",
    "time_of_day",
]


def normalize_schema(df):
    """Rename to the §4 contract, enforce dtypes, return the contract columns.

    The ``pu_borough``/``do_borough`` and zone helper columns added in integrate
    are NOT part of the trips contract — boroughs/zones live in Gary's separate
    zones dimension — so they are dropped here by selecting only CONTRACT_COLUMNS.
    """
    df = df.rename(columns=RENAME_MAP)

    # Enforce final dtypes. Nullable Int64/Float64 from load/clean collapse to
    # plain int64/float64 here (cleaning guarantees the id/count columns are
    # non-null; float columns keep NaN for the guarded ratio features).
    for col in INT_COLUMNS:
        df[col] = df[col].astype("int64")
    for col in FLOAT_COLUMNS:
        df[col] = df[col].astype("float64")
    df["is_cross_borough"] = df["is_cross_borough"].astype(bool)
    for col in STRING_COLUMNS:
        df[col] = df[col].astype("string")
    for col in DATETIME_COLUMNS:
        df[col] = pd.to_datetime(df[col])

    # Select exactly the contract columns in order (drops borough/zone helpers).
    return df[CONTRACT_COLUMNS].copy()
