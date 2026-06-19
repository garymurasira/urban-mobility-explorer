# Stage 1: load raw taxi CSV with explicit dtypes + parsed datetimes.

from pathlib import Path

import pandas as pd

RAW_PATH = Path("data/raw/yellow_tripdata_2019-01.csv")
DATETIME_COLUMNS = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]

# nullable Int64/Float64 where the file has blanks; raw TLC names kept here.
DTYPES = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "RatecodeID": "Int64",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "store_and_fwd_flag": "string",
    "trip_distance": "float64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "Float64",
}


def load_trips(path=RAW_PATH, nrows=None, chunksize=None):
    # chunksize -> iterator of chunks; otherwise a single DataFrame.
    return pd.read_csv(
        path,
        dtype=DTYPES,
        parse_dates=DATETIME_COLUMNS,
        nrows=nrows,
        chunksize=chunksize,
    )
