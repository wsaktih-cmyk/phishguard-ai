import psycopg
import pandas as pd

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "siem_db",
    "user": "postgres",
    "password": "wishter22"
}

conn = psycopg.connect(**DB_CONFIG)

query = """
SELECT
    id,
    timestamp,
    source_ip,
    destination_ip,
    source_port,
    destination_port,
    protocol,
    event_type,
    username,
    status,
    severity
FROM events
"""

df = pd.read_sql(query, conn)

conn.close()

print("Jumlah event:", len(df))
print()
print(df.head(10))