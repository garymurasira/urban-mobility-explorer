"""Stage 1 — Load.

Read the raw NYC Yellow Taxi CSV (`yellow_tripdata_2019-01.csv`, ~7.67M rows)
with explicit dtypes and parse the pickup/dropoff datetime columns.

Column names are kept exactly as the TLC ships them at this stage (CamelCase
like ``VendorID``/``PULocationID``); renaming to the snake_case output contract
(CLAUDE.md §4) happens later in the normalization stage, not here.

Nullable dtypes (``Int64``/``Float64``) are used for columns that contain blanks
in the January 2019 file — notably ``passenger_count``, ``RatecodeID`` and
``congestion_surcharge`` — so empty cells become ``pd.NA`` instead of forcing the
whole column to float or raising on parse.

Memory note: the full file is ~657 MB / 7.67M rows. ``load_trips`` accepts
``nrows`` (cap rows) and ``chunksize`` (stream an iterator of DataFrames) so the
file can be processed without holding it all in memory.

Input:  data/raw/yellow_tripdata_2019-01.csv  (git-ignored)
Output: a DataFrame (or an iterator of DataFrame chunks if ``chunksize`` is set).
"""

from pathlib import Path

import pandas as pd

# Default raw input location (git-ignored). Resolved relative to the repo root.
RAW_PATH = Path("data/raw/yellow_tripdata_2019-01.csv")

# Datetime columns parsed on read.
DATETIME_COLUMNS = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]

# Explicit per-column dtypes. Nullable integer/float (Int64/Float64) is used
# wherever the January 2019 file carries blanks, so missing values survive as
# pd.NA rather than coercing the column or breaking the load.
DTYPES = {
    # Identifiers / categorical codes — nullable integers.
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "RatecodeID": "Int64",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    # Flag — kept as a string ('Y'/'N').
    "store_and_fwd_flag": "string",
    # Distance and itemized fare columns — floats.
    "trip_distance": "float64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    # Mostly blank in Jan 2019 — nullable float keeps decimals and NA.
    "congestion_surcharge": "Float64",
}


def load_trips(path=RAW_PATH, nrows=None, chunksize=None):
    """Read the raw trip CSV with a typed schema and parsed datetimes.

    Args:
        path: CSV path. Defaults to the git-ignored raw file (``RAW_PATH``).
        nrows: optional cap on rows read (handy for sampling/verification).
        chunksize: if set, return an iterator yielding DataFrame chunks of this
            size instead of a single in-memory DataFrame.

    Returns:
        A ``pandas.DataFrame``, or a ``TextFileReader`` iterator of DataFrame
        chunks when ``chunksize`` is provided.
    """
    return pd.read_csv(
        path,
        dtype=DTYPES,
        parse_dates=DATETIME_COLUMNS,
        nrows=nrows,
        chunksize=chunksize,
    )
