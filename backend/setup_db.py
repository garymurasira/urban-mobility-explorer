import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

schema_path = os.path.join(os.path.dirname(__file__), "..", "database", "schema.sql")

cnx = mysql.connector.connect(
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
)
cur = cnx.cursor()

with open(schema_path) as f:
    sql = f.read()

for statement in sql.split(";"):
    if statement.strip():
        cur.execute(statement)

cnx.commit()
cur.close()
cnx.close()
print("Tables created in", os.environ["DB_NAME"])