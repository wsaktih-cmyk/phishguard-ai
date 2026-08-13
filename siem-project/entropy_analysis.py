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
    """
    Menghitung Shannon Entropy.
    Semakin tinggi nilainya, semakin beragam pola datanya.
    """
    if not values:
        return 0.0

    counts = Counter(values)
    total = len(values)

    entropy = 0.0

    for count in counts.values():
        probability = count / total
        entropy -= probability * math.log2(probability)

    return entropy


# Koneksi PostgreSQL
conn = psycopg.connect(**DB_CONFIG)

query = """
SELECT
    id,
    source_ip,
    destination_port,
    protocol,
    event_type,
    status
FROM events
"""

df = pd.read_sql(query, conn)

conn.close()


# Hitung entropy berdasarkan aktivitas setiap source IP
results = []

for ip, group in df.groupby("source_ip"):

    event_entropy = shannon_entropy(
        group["event_type"].tolist()
    )

    port_entropy = shannon_entropy(
        group["destination_port"].tolist()
    )

    protocol_entropy = shannon_entropy(
        group["protocol"].tolist()
    )

    status_entropy = shannon_entropy(
        group["status"].tolist()
    )

    results.append({
        "source_ip": str(ip),
        "event_entropy": event_entropy,
        "port_entropy": port_entropy,
        "protocol_entropy": protocol_entropy,
        "status_entropy": status_entropy,
        "event_count": len(group)
    })


result_df = pd.DataFrame(results)

print("\n=== SHANNON ENTROPY ANALYSIS ===\n")

print(
    result_df
    .sort_values("event_entropy", ascending=False)
    .head(20)
    .to_string(index=False)
)