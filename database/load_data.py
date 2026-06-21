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
           (2, "VeriFone Inc."),
           (4, "Dependable Driver Systems"),]

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

ZONES_CSV_PATH  = os.path.join(os.path.dirname(__file__), "..", "data", "sample", "zones_reference.csv")
TRIPS_CSV_PATH  = os.path.join(os.path.dirname(__file__), "..", "data", "sample", "trips_clean_sample.csv")
BATCH_SIZE      = 1000


def truncate_all_tables(cursor):
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in ["trips", "zones", "vendors", "rate_codes", "payment_types"]:
        cursor.execute(f"TRUNCATE TABLE {table}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    print("All tables cleared.")


def load_zones(cursor):
    insert_sql = """
        INSERT INTO zones (location_id, borough, zone, service_zone, centroid_lat, centroid_lon)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    rows = []
    with open(ZONES_CSV_PATH, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            rows.append((
                int(row["location_id"]),
                row["borough"],
                row["zone"],
                row["service_zone"],
                to_float(row["centroid_lat"]),
                to_float(row["centroid_lon"]),
            ))
    cursor.executemany(insert_sql, rows)
    print(f"zones: {cursor.rowcount} rows loaded.")


def load_vendors(cursor):
    insert_sql = "INSERT INTO vendors (vendor_id, vendor_name) VALUES (%s, %s)"
    cursor.executemany(insert_sql, VENDORS)
    print(f"vendors: {cursor.rowcount} rows loaded.")


def load_rate_codes(cursor):
    insert_sql = "INSERT INTO rate_codes (rate_code_id, description) VALUES (%s, %s)"
    cursor.executemany(insert_sql, RATE_CODES)
    print(f"rate_codes: {cursor.rowcount} rows loaded.")


def load_payment_types(cursor):
    insert_sql = "INSERT INTO payment_types (payment_type_id, description) VALUES (%s, %s)"
    cursor.executemany(insert_sql, PAYMENT_TYPES)
    print(f"payment_types: {cursor.rowcount} rows loaded.")


def to_int(value):
    if value == "" or value is None:
        return None
    return int(float(value))


def to_float(value):
    if value == "" or value is None:
        return None
    return float(value)


def to_bool(value):
    if value == "" or value is None:
        return None
    return 1 if value.strip().lower() == "true" else 0


def build_trip_record(row):
    return (
        to_int(row["vendor_id"]),
        row["pickup_datetime"],
        row["dropoff_datetime"],
        to_int(row["passenger_count"]),
        to_float(row["trip_distance"]),
        to_int(row["rate_code_id"]),
        to_int(row["pu_location_id"]),
        to_int(row["do_location_id"]),
        to_int(row["payment_type"]),
        to_float(row["fare_amount"]),
        to_float(row["extra"]),
        to_float(row["mta_tax"]),
        to_float(row["tip_amount"]),
        to_float(row["tolls_amount"]),
        to_float(row["improvement_surcharge"]),
        to_float(row["congestion_surcharge"]),
        to_float(row["total_amount"]),
        to_float(row["trip_duration_min"]),
        to_float(row["avg_speed_mph"]),
        to_float(row["fare_per_mile"]),
        to_float(row["tip_pct"]),
        to_bool(row["is_cross_borough"]),
        to_int(row["pickup_hour"]),
        to_int(row["pickup_day_of_week"]),
    )


INSERT_TRIP_SQL = """
    INSERT INTO trips (
        vendor_id, pickup_datetime, dropoff_datetime, passenger_count,
        trip_distance, rate_code_id, pu_location_id, do_location_id,
        payment_type_id, fare_amount, extra, mta_tax, tip_amount,
        tolls_amount, improvement_surcharge, congestion_surcharge,
        total_amount, trip_duration_min, avg_speed_mph, fare_per_mile,
        tip_pct, is_cross_borough, pickup_hour, day_of_week
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
"""


def insert_batch(cursor, batch):
    success = 0
    failed = 0
    try:
        cursor.executemany(INSERT_TRIP_SQL, batch)
        success = len(batch)
    except mysql.connector.Error:
        for record in batch:
            try:
                cursor.execute(INSERT_TRIP_SQL, record)
                success += 1
            except mysql.connector.Error as error:
                print(f"  Row skipped: {error}")
                failed += 1
    return success, failed


def load_trips(cursor):
    total_success = 0
    total_failed  = 0
    batch         = []

    with open(TRIPS_CSV_PATH, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            batch.append(build_trip_record(row))
            if len(batch) == BATCH_SIZE:
                success, failed = insert_batch(cursor, batch)
                total_success  += success
                total_failed   += failed
                batch           = []

        if batch:
            success, failed = insert_batch(cursor, batch)
            total_success  += success
            total_failed   += failed

    print(f"trips: {total_success} rows loaded, {total_failed} rows failed.")


def main():
    print("Connecting to database...")
    connection = get_connection()
    cursor = connection.cursor()

    print("Clearing existing data...")
    truncate_all_tables(cursor)

    print("Loading dimension tables...")
    load_zones(cursor)
    load_vendors(cursor)
    load_rate_codes(cursor)
    load_payment_types(cursor)

    print("Loading trips...")
    load_trips(cursor)

    connection.commit()
    cursor.close()
    connection.close()
    print("Done.")


if __name__ == "__main__":
    main()
