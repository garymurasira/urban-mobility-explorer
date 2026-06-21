from flask import Flask, jsonify
from routes.insights import insights_bp
from flask_cors import CORS

from db import get_connection
from routes.stats import stats_bp

from routes.trips import trips_bp 
from routes.zones import zones_bp



def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(stats_bp) 
    app.register_blueprint(trips_bp)  
    app.register_blueprint(zones_bp)
    app.register_blueprint(insights_bp)

    @app.route("/api/health")
    def health():
        """Confirms the API is running and can reach the database."""
        try:
            connection = get_connection()
            connection.close()
            db_status = "connected"
        except Exception as error:
            db_status = f"error: {error}"
        return jsonify({"status": "ok", "database": db_status})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)