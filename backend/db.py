import os
from decimal import Decimal
from datetime import datetime, date

import mysql.connector
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


def get_connection():
    host = os.environ["DB_HOST"].strip()
    port = int(str(os.environ["DB_PORT"]).strip())

    return mysql.connector.connect(
        host=host,
        port=port,
        database=os.environ["DB_NAME"].strip(),
        user=os.environ["DB_USER"].strip(),
        password=os.environ["DB_PASSWORD"].strip(),
    )
def _json_safe(value):
    """Convert DB types that JSON can't handle into plain types."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def run_query(sql, params=None, connection=None):
    close_conn = False

    if connection is None:
        connection = get_connection()
        close_conn = True

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        return [{k: _json_safe(v) for k, v in row.items()} for row in rows]
    finally:
        cursor.close()
        if close_conn:
            connection.close()