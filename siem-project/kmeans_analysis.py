import psycopg
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "siem_db",
    "user": "postgres",
    "password": "wishter22"
}


# =========================
# 1. Ambil data entropy
# =========================

conn = psycopg.connect(**DB_CONFIG)

query = """
SELECT
    id,
    source_ip,
    event_entropy,
    port_entropy,
    protocol_entropy,
    status_entropy,
    event_count
FROM entropy_results
"""

df = pd.read_sql(query, conn)

conn.close()


if len(df) < 3:
    print("Data terlalu sedikit untuk K-Means.")
    print("Jumlah data:", len(df))
    exit()


# =========================
# 2. Pilih fitur
# =========================

features = [
    "event_entropy",
    "port_entropy",
    "protocol_entropy",
    "status_entropy",
    "event_count"
]

X = df[features].fillna(0)


# =========================
# 3. Normalisasi
# =========================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# =========================
# 4. K-Means
# =========================

kmeans = KMeans(
    n_clusters=3,
    random_state=42,
    n_init=10
)

df["cluster"] = kmeans.fit_predict(X_scaled)


# =========================
# 5. Hitung jarak ke pusat cluster
# =========================

distances = kmeans.transform(X_scaled)

df["distance"] = distances.min(axis=1)


# =========================
# 6. Tampilkan hasil
# =========================

print("\n=== K-MEANS ANALYSIS ===\n")

print(
    df[
        [
            "source_ip",
            "event_entropy",
            "port_entropy",
            "protocol_entropy",
            "status_entropy",
            "event_count",
            "cluster",
            "distance"
        ]
    ]
    .sort_values("distance", ascending=False)
    .head(20)
    .to_string(index=False)
)

print("\nJumlah data:", len(df))

print("\nDistribusi cluster:")

print(
    df["cluster"]
    .value_counts()
    .sort_index()
)