"""Stage 3 — Clean.

Apply explicit, defensible data-integrity rules and log every removal to
`data/exclusion_log.csv` (one row per rule with a removal count):
- missing values (passenger_count, congestion_surcharge, RatecodeID);
- exact duplicate trips;
- invalid records: dropoff before pickup, non-positive distance/fare,
  implausible passenger_count, impossible avg speed, out-of-January timestamps.

Input:  enriched trips DataFrame.
Output: cleaned trips DataFrame (+ the exclusion log written to disk).
"""

# import pandas as pd


def clean_trips(trips):
    """Handle missing values, drop duplicates and outliers, log exclusions."""
    # TODO: apply integrity rules; record per-rule removal counts
    raise NotImplementedError
