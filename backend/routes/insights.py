from flask import Blueprint, jsonify
from db import run_query

insights_bp = Blueprint("insights", __name__)


@insights_bp.route("/api/insights", methods=["GET"])
def insights():
    peak_hour = run_query("""
        SELECT pickup_hour, COUNT(*) AS trip_count
        FROM trips WHERE pickup_hour IS NOT NULL
        GROUP BY pickup_hour ORDER BY trip_count DESC LIMIT 1
    """)

    cross = run_query("""
        SELECT SUM(CASE WHEN is_cross_borough = 1 THEN 1 ELSE 0 END) AS cross_trips,
               COUNT(*) AS total_trips
        FROM trips
    """)

    tips = run_query("""
        SELECT payment_type_id, AVG(tip_pct) AS avg_tip_pct, COUNT(*) AS trip_count
        FROM trips WHERE tip_pct IS NOT NULL
        GROUP BY payment_type_id ORDER BY avg_tip_pct DESC
    """)

    return jsonify({
        "peak_hour": peak_hour[0] if peak_hour else None,
        "cross_borough": cross[0] if cross else None,
        "tips_by_payment": tips,
    })