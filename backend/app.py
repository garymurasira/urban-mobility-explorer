from flask import Flask, jsonify
from flask_cors import CORS

from db import get_connection
from routes.stats import stats_bp


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(stats_bp)

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