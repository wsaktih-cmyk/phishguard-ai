import psycopg
import pandas as pd
import math
from collections import Counter


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "siem_db",
    "user": "postgres",
    "password": "wishter22"
}


def shannon_entropy(values):
    if not values:
        return 0.0

    counts = Counter(values)
    total = len(values)

    entropy = 0.0

    for count in counts.values():
        probability = count / total
        entropy -= probability * math.log2(probability)

    return entropy


conn = psycopg.connect(**DB_CONFIG)


query = """
SELECT
    source_ip,
    destination_port,
    protocol,
    event_type,
    status
FROM events
"""

df = pd.read_sql(query, conn)


results = []

for ip, group in df.groupby("source_ip"):

    results.append({
        "source_ip": str(ip),
        "event_entropy": shannon_entropy(
            group["event_type"].tolist()
        ),
        "port_entropy": shannon_entropy(
            group["destination_port"].tolist()
        ),
        "protocol_entropy": shannon_entropy(
            group["protocol"].tolist()
        ),
        "status_entropy": shannon_entropy(
            group["status"].tolist()
        ),
        "event_count": len(group)
    })


insert_query = """
INSERT INTO entropy_results (
    source_ip,
    event_entropy,
    port_entropy,
    protocol_entropy,
    status_entropy,
    event_count
)
VALUES (
    %s, %s, %s, %s, %s, %s
)
"""


with conn.cursor() as cursor:

    for result in results:
        cursor.execute(
            insert_query,
            (
                result["source_ip"],
                result["event_entropy"],
                result["port_entropy"],
                result["protocol_entropy"],
                result["status_entropy"],
                result["event_count"]
            )
        )

conn.commit()
conn.close()


print("=== ANALISIS SELESAI ===")
print(f"Jumlah IP dianalisis: {len(results)}")
print("Hasil entropy berhasil disimpan ke PostgreSQL.")