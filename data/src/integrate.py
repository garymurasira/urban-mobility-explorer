"""Stage 2 — Integrate.

Attach geographic context to each trip:
- join `taxi_zone_lookup.csv` on PULocationID / DOLocationID to add pickup and
  dropoff borough + zone names;
- read the `taxi_zones` shapefile (geopandas) and compute each zone's centroid
  lat/lon for mapping and distance features.

Input:  raw trips DataFrame + data/raw/taxi_zone_lookup.csv + data/raw/taxi_zones/
Output: trips DataFrame enriched with borough/zone and centroid columns.
"""

# import pandas as pd
# import geopandas as gpd


def integrate_zones(trips):
    """Join zone lookup and shapefile centroids onto the trips DataFrame."""
    # TODO: merge taxi_zone_lookup on PU/DO LocationID; compute zone centroids
    raise NotImplementedError
