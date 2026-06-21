from flask import Blueprint, jsonify, request
from db import run_query

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("/api/stats/summary", methods=["GET"])
def summary():
    """Dashboard summary statistics with optional filters."""

    args = request.args

    where = []
    params = []

    # Date filters
    if args.get("date_from"):
        where.append("pickup_datetime >= %s")
        params.append(args.get("date_from"))

    if args.get("date_to"):
        where.append("pickup_datetime <= %s")
        params.append(args.get("date_to"))

    # Borough filter
    if args.get("borough"):
        where.append("""
            pu_location_id IN (
                SELECT location_id
                FROM zones
                WHERE borough = %s
            )
        """)
        params.append(args.get("borough"))

    where_sql = ""
    if where:
        where_sql = "WHERE " + " AND ".join(where)

    sql = f"""
        SELECT
            COUNT(*) AS total_trips,
            ROUND(SUM(total_amount), 2) AS total_revenue,
            ROUND(AVG(fare_amount), 2) AS avg_fare,
            ROUND(AVG(trip_distance), 2) AS avg_trip_distance,
            ROUND(AVG(trip_duration_min), 2) AS avg_duration_min,
            ROUND(AVG(avg_speed_mph), 2) AS avg_speed_mph,
            ROUND(AVG(tip_pct), 4) AS avg_tip_pct,

            ROUND(
                AVG(
                    CASE
                        WHEN is_cross_borough = 1 THEN 100
                        ELSE 0
                    END
                ),
                2
            ) AS pct_cross_borough

        FROM trips

        {where_sql}
    """

    result = run_query(sql, params)

    if result:
        return jsonify(result[0])

    return jsonify({})


@stats_bp.route("/api/stats/hourly", methods=["GET"])
def hourly_stats():
    rows = run_query("""
        SELECT
            day_of_week,
            pickup_hour,
            COUNT(*) AS trip_count,
            ROUND(AVG(fare_amount), 2) AS avg_fare,
            ROUND(AVG(trip_distance), 2) AS avg_distance
        FROM trips
        WHERE pickup_hour IS NOT NULL
          AND day_of_week IS NOT NULL
        GROUP BY day_of_week, pickup_hour
        ORDER BY day_of_week, pickup_hour
    """)

    return jsonify(rows)