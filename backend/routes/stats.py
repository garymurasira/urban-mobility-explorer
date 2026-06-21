from flask import Blueprint, jsonify

from db import run_query

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("/api/stats/summary")
def summary():
    """High-level KPIs across all trips, for the dashboard summary cards."""
    sql = """
        SELECT
            COUNT(*)                          AS total_trips,
            ROUND(SUM(total_amount), 2)       AS total_revenue,
            ROUND(AVG(fare_amount), 2)        AS avg_fare,
            ROUND(AVG(trip_distance), 2)      AS avg_trip_distance,
            ROUND(AVG(trip_duration_min), 2)  AS avg_duration_min,
            ROUND(AVG(avg_speed_mph), 2)      AS avg_speed_mph,
            ROUND(AVG(tip_pct), 4)            AS avg_tip_pct
        FROM trips
    """
    result = run_query(sql)
    return jsonify(result[0] if result else {})

@stats_bp.route("/api/stats/hourly", methods=["GET"])
def hourly_stats():
    rows = run_query("""
        SELECT day_of_week, pickup_hour,
               COUNT(*) AS trip_count,
               AVG(fare_amount) AS avg_fare,
               AVG(trip_distance) AS avg_distance
        FROM trips
        WHERE pickup_hour IS NOT NULL AND day_of_week IS NOT NULL
        GROUP BY day_of_week, pickup_hour
        ORDER BY day_of_week, pickup_hour
    """)
    return jsonify(rows)