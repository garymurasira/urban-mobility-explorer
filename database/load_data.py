import os
import csv
import mysql.connector
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


def get_connection():
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


VENDORS = [(1, "Creative Mobile Technologies"),
           (2, "VeriFone Inc."),]

RATE_CODES = [(1,  "Standard rate"),
              (2,  "JFK"),
              (3,  "Newark"),
              (4,  "Nassau or Westchester"),
              (5,  "Negotiated fare"),
              (6,  "Group ride"),
              (99, "Unknown"),]

PAYMENT_TYPES = [(1, "Credit card"),
                 (2, "Cash"),
                 (3, "No charge"),
                 (4, "Dispute"),
                 (5, "Unknown"),
                 (6, "Voided trip"),]
