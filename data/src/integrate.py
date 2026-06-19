"""Stage 2 — Integrate.

Attach geographic context to each trip:
- join `taxi_zone_lookup.csv` on PULocationID / DOLocationID to add pickup and
  dropoff borough + zone names;
- read the `taxi_zones` shapefile (geopandas) and compute each zone's centroid
  lat/lon for mapping and distance features.

Trip column names are kept exactly as the TLC ships them at this stage
(``PULocationID``/``DOLocationID``); renaming to the snake_case output contract
(CLAUDE.md §4) happens later in normalization, not here.

Input:  raw trips DataFrame + data/raw/taxi_zone_lookup.csv + data/raw/taxi_zones/
Output: trips DataFrame enriched with borough/zone columns; a centroid table.
"""

from pathlib import Path

import geopandas as gpd
import pandas as pd

# Default raw input locations (git-ignored).
ZONE_LOOKUP_PATH = Path("data/raw/taxi_zone_lookup.csv")
ZONE_SHAPEFILE_PATH = Path("data/raw/taxi_zones/taxi_zones.shp")

# The TLC shapefile ships in NY State Plane (feet); reproject to WGS84 degrees
# before computing centroids so lat/lon come out in degrees.
SHAPEFILE_CRS = 2263
WGS84_CRS = 4326


def load_zone_lookup(path=ZONE_LOOKUP_PATH):
    """Read the taxi zone lookup table.

    Columns: ``LocationID``, ``Borough``, ``Zone``, ``service_zone``.
    """
    return pd.read_csv(path)


def attach_zones(trips_df, zones_df):
    """Left-join borough/zone info onto trips for both pickup and dropoff.

    The lookup is merged twice — once on ``PULocationID`` and once on
    ``DOLocationID`` — producing the prefixed columns ``pu_borough``,
    ``pu_zone``, ``pu_service_zone`` and ``do_borough``, ``do_zone``,
    ``do_service_zone``. Left joins keep every trip: unmatched IDs (e.g. 264/265
    "Unknown") survive with null zone columns and are handled in cleaning.

    Args:
        trips_df: trips DataFrame with raw ``PULocationID``/``DOLocationID``.
        zones_df: the lookup DataFrame from ``load_zone_lookup``.

    Returns:
        A new DataFrame with the six pickup/dropoff zone columns added.
    """
    # Pickup-side lookup: rename to pu_* and key on LocationID.
    pu_zones = zones_df.rename(
        columns={
            "LocationID": "PULocationID",
            "Borough": "pu_borough",
            "Zone": "pu_zone",
            "service_zone": "pu_service_zone",
        }
    )
    # Dropoff-side lookup: rename to do_* and key on LocationID.
    do_zones = zones_df.rename(
        columns={
            "LocationID": "DOLocationID",
            "Borough": "do_borough",
            "Zone": "do_zone",
            "service_zone": "do_service_zone",
        }
    )

    merged = trips_df.merge(pu_zones, on="PULocationID", how="left")
    merged = merged.merge(do_zones, on="DOLocationID", how="left")
    return merged


def load_zone_centroids(shp_path=ZONE_SHAPEFILE_PATH):
    """Compute each zone's centroid latitude/longitude from the shapefile.

    The shapefile is in a projected CRS (EPSG:2263, NY State Plane in feet); it
    is reprojected to EPSG:4326 *before* computing centroids so the result is in
    geographic degrees. ``LocationID`` matches the lookup IDs.

    Returns:
        DataFrame with ``location_id``, ``centroid_lat``, ``centroid_lon``.
    """
    gdf = gpd.read_file(shp_path)

    # Reproject to WGS84 degrees before taking centroids (per the assignment).
    gdf = gdf.to_crs(WGS84_CRS)
    centroids = gdf.geometry.centroid

    return pd.DataFrame(
        {
            "location_id": gdf["LocationID"].astype("int64"),
            "centroid_lat": centroids.y,
            "centroid_lon": centroids.x,
        }
    ).reset_index(drop=True)
