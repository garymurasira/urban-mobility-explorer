from flask import Blueprint, request, jsonify
from db import run_query
from algorithms.topk import top_n_by_count

zones_bp = Blueprint("zones", __name__)


@zones_bp.route("/api/zones/top", methods=["GET"])
def top_zones():
    direction = request.args.get("direction", "pickup")
    limit = request.args.get("limit", default=10, type=int)
    limit = max(1, min(limit, 50))

    column = "pu_location_id" if direction == "pickup" else "do_location_id"

    rows = run_query(f"SELECT {column} AS zone_id FROM trips")
    ranked = top_n_by_count(((r["zone_id"], 1) for r in rows), limit)

    zone_rows = run_query(
        "SELECT location_id, borough, zone, centroid_lat, centroid_lon FROM zones"
    )
    lookup = {z["location_id"]: z for z in zone_rows}

    results = [{
        "location_id": zid,
        "borough": lookup.get(zid, {}).get("borough"),
        "zone": lookup.get(zid, {}).get("zone"),
        "lat": lookup.get(zid, {}).get("centroid_lat"),
        "lon": lookup.get(zid, {}).get("centroid_lon"),
        "trip_count": count,
    } for zid, count in ranked]

    return jsonify({"direction": direction, "limit": limit, "results": results})