# Stage 2: attach borough/zone via lookup join + zone centroids from shapefile.

from pathlib import Path

import geopandas as gpd
import pandas as pd

ZONE_LOOKUP_PATH = Path("data/raw/taxi_zone_lookup.csv")
ZONE_SHAPEFILE_PATH = Path("data/raw/taxi_zones/taxi_zones.shp")
SHAPEFILE_CRS = 2263
WGS84_CRS = 4326


def load_zone_lookup(path=ZONE_LOOKUP_PATH):
    return pd.read_csv(path)


def attach_zones(trips_df, zones_df):
    # left-join the lookup twice (PU and DO) so unmatched IDs survive as null.
    pu_zones = zones_df.rename(
        columns={
            "LocationID": "PULocationID",
            "Borough": "pu_borough",
            "Zone": "pu_zone",
            "service_zone": "pu_service_zone",
        }
    )
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
    gdf = gpd.read_file(shp_path)
    # dissolve multi-polygon zones (e.g. 56, 103) so each LocationID is unique.
    gdf = gdf.dissolve(by="LocationID").reset_index()
    # reproject to WGS84 degrees before taking centroids.
    gdf = gdf.to_crs(WGS84_CRS)
    centroids = gdf.geometry.centroid
    return pd.DataFrame(
        {
            "location_id": gdf["LocationID"].astype("int64"),
            "centroid_lat": centroids.y,
            "centroid_lon": centroids.x,
        }
    ).reset_index(drop=True)
