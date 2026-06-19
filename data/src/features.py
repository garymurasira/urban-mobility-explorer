# Stage 4: derive contract features (guarded divisions) + normalize to schema.

import numpy as np
import pandas as pd

PICKUP_COL = "tpep_pickup_datetime"
DROPOFF_COL = "tpep_dropoff_datetime"
CARD_PAYMENT_TYPE = 1  # tip_pct is card-only (TLC doesn't record cash tips)

# time_of_day buckets; uncovered hours (00-05, 22-23) fall to night.
MORNING_HOURS = range(6, 12)
AFTERNOON_HOURS = range(12, 17)
EVENING_HOURS = range(17, 22)


def _time_of_day(hour):
    conditions = [
        hour.isin(list(MORNING_HOURS)),
        hour.isin(list(AFTERNOON_HOURS)),
        hour.isin(list(EVENING_HOURS)),
    ]
    choices = ["morning", "afternoon", "evening"]
    return np.select(conditions, choices, default="night")


def add_features(df):
    df = df.copy()

    duration = df[DROPOFF_COL] - df[PICKUP_COL]
    duration_min = duration.dt.total_seconds() / 60.0
    df["trip_duration_min"] = duration_min.astype("float64")

    # .where guards every division so a zero denominator yields NaN, not inf.
    duration_hours = duration_min / 60.0
    df["avg_speed_mph"] = (df["trip_distance"] / duration_hours).where(
        duration_hours > 0
    )
    df["fare_per_mile"] = (df["fare_amount"] / df["trip_distance"]).where(
        df["trip_distance"] > 0
    )
    is_card = df["payment_type"] == CARD_PAYMENT_TYPE
    df["tip_pct"] = (df["tip_amount"] / df["fare_amount"]).where(
        is_card & (df["fare_amount"] > 0)
    )

    # cross-borough only when both boroughs are known and differ.
    both_known = df["pu_borough"].notna() & df["do_borough"].notna()
    df["is_cross_borough"] = (df["pu_borough"] != df["do_borough"]) & both_known

    df["pickup_hour"] = df[PICKUP_COL].dt.hour
    df["pickup_day_of_week"] = df[PICKUP_COL].dt.dayofweek  # 0=Mon .. 6=Sun
    df["time_of_day"] = _time_of_day(df["pickup_hour"])

    return df


# Schema contract (CLAUDE.md §4)
RENAME_MAP = {
    "VendorID": "vendor_id",
    "tpep_pickup_datetime": "pickup_datetime",
    "tpep_dropoff_datetime": "dropoff_datetime",
    "RatecodeID": "rate_code_id",
    "PULocationID": "pu_location_id",
    "DOLocationID": "do_location_id",
}

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
    df = df.rename(columns=RENAME_MAP)
    for col in INT_COLUMNS:
        df[col] = df[col].astype("int64")
    for col in FLOAT_COLUMNS:
        df[col] = df[col].astype("float64")
    df["is_cross_borough"] = df["is_cross_borough"].astype(bool)
    for col in STRING_COLUMNS:
        df[col] = df[col].astype("string")
    for col in DATETIME_COLUMNS:
        df[col] = pd.to_datetime(df[col])
    # select contract columns in order (drops borough/zone helpers).
    return df[CONTRACT_COLUMNS].copy()
