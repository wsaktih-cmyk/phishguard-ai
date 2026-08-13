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

if len(df) < 3:
    print("Data tidak cukup.")
    conn.close()
    exit()


features = [
    "event_entropy",
    "port_entropy",
    "protocol_entropy",
    "status_entropy",
    "event_count"
]

X = df[features].fillna(0)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


kmeans = KMeans(
    n_clusters=3,
    random_state=42,
    n_init=10
)

df["cluster"] = kmeans.fit_predict(X_scaled)

distances = kmeans.transform(X_scaled)

df["distance"] = distances.min(axis=1)


# Normalisasi distance menjadi 0-1
max_distance = df["distance"].max()

if max_distance == 0:
    df["anomaly_score"] = 0
else:
    df["anomaly_score"] = (
        df["distance"] / max_distance
    )


# Tentukan severity
def get_severity(score):

    if score >= 0.80:
        return "CRITICAL"

    elif score >= 0.60:
        return "HIGH"

    elif score >= 0.40:
        return "MEDIUM"

    return "LOW"


df["severity"] = df["anomaly_score"].apply(get_severity)


# Simpan hasil K-Means
insert_kmeans = """
INSERT INTO kmeans_results (
    source_ip,
    cluster,
    distance,
    anomaly_score
)
VALUES (%s, %s, %s, %s)
"""


# Simpan alert untuk aktivitas HIGH/CRITICAL
insert_alert = """
INSERT INTO alerts (
    source_ip,
    anomaly_score,
    severity,
    alert_type,
    description
)
VALUES (%s, %s, %s, %s, %s)
"""


with conn.cursor() as cursor:

    for _, row in df.iterrows():

        cursor.execute(
            insert_kmeans,
            (
                str(row["source_ip"]),
                int(row["cluster"]),
                float(row["distance"]),
                float(row["anomaly_score"])
            )
        )

        if row["anomaly_score"] >= 0.60:

            cursor.execute(
                insert_alert,
                (
                    str(row["source_ip"]),
                    float(row["anomaly_score"]),
                    row["severity"],
                    "ANOMALOUS_ACTIVITY",
                    "Aktivitas memiliki karakteristik yang berbeda dari mayoritas data."
                )
            )


conn.commit()
conn.close()


print("=== ANOMALY DETECTION SELESAI ===")
print(f"Total IP dianalisis : {len(df)}")
print(
    f"High/Critical      : "
    f"{len(df[df['anomaly_score'] >= 0.60])}"
)

print("\nTop 10 anomaly:")

print(
    df[
        [
            "source_ip",
            "cluster",
            "anomaly_score",
            "severity"
        ]
    ]
    .sort_values(
        "anomaly_score",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)