"""Stage 1 — Load.

Read the raw NYC Yellow Taxi CSV (`yellow_tripdata_2019-01.csv`, ~7.67M rows)
with explicit dtypes and parse the pickup/dropoff datetime columns. Chunked
reading will be used if memory is tight.

Input:  data/raw/yellow_tripdata_2019-01.csv  (git-ignored)
Output: an in-memory DataFrame handed to the integrate stage.
"""

# import pandas as pd


def load_trips():
    """Read the raw trip CSV with typed schema and parsed datetimes.

    Returns the raw trips DataFrame for downstream stages.
    """
    # TODO: read_csv with explicit dtypes; parse tpep_pickup/dropoff_datetime
    raise NotImplementedError
