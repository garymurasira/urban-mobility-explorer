import os
from decimal import Decimal
from datetime import datetime, date

import mysql.connector
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


def get_connection():
    """Open a new connection to the MySQL database using .env credentials."""
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def _json_safe(value):
    """Convert DB types that JSON can't handle into plain types."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def run_query(sql, params=None):
    """Run a SELECT and return rows as a list of JSON-safe dictionaries."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        return [{key: _json_safe(val) for key, val in row.items()} for row in rows]
    finally:
        cursor.close()
        connection.close()