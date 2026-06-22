from flask import Blueprint, request, jsonify
from db import run_query, get_connection

trips_bp = Blueprint("trips", __name__)

SORTABLE = {
    "pickup_datetime", "dropoff_datetime", "trip_distance",
    "fare_amount", "total_amount", "tip_amount",
    "trip_duration_min", "avg_speed_mph", "passenger_count",
}


@trips_bp.route("/api/trips", methods=["GET"])
def list_trips():
    a = request.args

    page = max(1, a.get("page", default=1, type=int))
    page_size = min(max(a.get("page_size", default=25, type=int), 1), 100)
    offset = (page - 1) * page_size

    where, params = [], []

    def add(cond, val):
        where.append(cond)
        params.append(val)

    if a.get("start_date"):
        add("t.pickup_datetime >= %s", a["start_date"])

    if a.get("end_date"):
        add("t.pickup_datetime <= %s", a["end_date"])

    if a.get("borough"):
        add("pz.borough = %s", a["borough"])

    if a.get("payment_type", type=int) is not None:
        add("t.payment_type_id = %s", a.get("payment_type", type=int))

    if a.get("min_distance", type=float) is not None:
        add("t.trip_distance >= %s", a.get("min_distance", type=float))

    if a.get("max_distance", type=float) is not None:
        add("t.trip_distance <= %s", a.get("max_distance", type=float))

    if a.get("min_fare", type=float) is not None:
        add("t.fare_amount >= %s", a.get("min_fare", type=float))

    if a.get("max_fare", type=float) is not None:
        add("t.fare_amount <= %s", a.get("max_fare", type=float))

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    sort_by = a.get("sort_by", "pickup_datetime")
    if sort_by not in SORTABLE:
        sort_by = "pickup_datetime"

    order = "ASC" if a.get("order", "desc").lower() == "asc" else "DESC"

    # 👇 single DB connection
    connection = get_connection()

    try:
        total = run_query(f"""
            SELECT COUNT(*) AS total
            FROM trips t
            JOIN zones pz ON t.pu_location_id = pz.location_id
            {where_sql}
        """, params, connection)[0]["total"]

        data = run_query(f"""
            SELECT t.trip_id, t.pickup_datetime, t.dropoff_datetime,
                   t.passenger_count, t.trip_distance, t.fare_amount,
                   t.tip_amount, t.total_amount, t.trip_duration_min, t.avg_speed_mph,
                   pz.borough AS pickup_borough, pz.zone AS pickup_zone,
                   dz.borough AS dropoff_borough, dz.zone AS dropoff_zone
            FROM trips t
            JOIN zones pz ON t.pu_location_id = pz.location_id
            JOIN zones dz ON t.do_location_id = dz.location_id
            {where_sql}
            ORDER BY t.{sort_by} {order}
            LIMIT %s OFFSET %s
        """, params + [page_size, offset], connection)

    finally:
        connection.close()

    return jsonify({
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size,
        "sort_by": sort_by,
        "order": order.lower(),
        "data": data,
    })