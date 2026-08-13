from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import psycopg

app = FastAPI()

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "siem_db",
    "user": "postgres",
    "password": "wishter22"
}


def get_connection():
    return psycopg.connect(**DB_CONFIG)


@app.get("/api/stats")
def stats():

    conn = get_connection()

    with conn.cursor() as cur:

        cur.execute("SELECT COUNT(*) FROM events")
        events = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM alerts")
        alerts = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*)
            FROM alerts
            WHERE severity = 'CRITICAL'
        """)
        critical = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*)
            FROM alerts
            WHERE severity = 'HIGH'
        """)
        high = cur.fetchone()[0]

    conn.close()

    return {
        "events": events,
        "alerts": alerts,
        "critical": critical,
        "high": high
    }


@app.get("/api/alerts")
def get_alerts():

    conn = get_connection()

    with conn.cursor() as cur:

        cur.execute("""
            SELECT
                source_ip,
                anomaly_score,
                severity,
                alert_type,
                created_at
            FROM alerts
            ORDER BY anomaly_score DESC
            LIMIT 20
        """)

        rows = cur.fetchall()

    conn.close()

    return [
        {
            "source_ip": str(row[0]),
            "anomaly_score": round(float(row[1]), 3),
            "severity": row[2],
            "alert_type": row[3],
            "created_at": str(row[4])
        }
        for row in rows
    ]


@app.get("/api/clusters")
def get_clusters():

    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                cluster,
                COUNT(*) AS total
            FROM kmeans_results
            GROUP BY cluster
            ORDER BY cluster
        """)

        rows = cur.fetchall()

    conn.close()

    return [
        {
            "cluster": row[0],
            "total": row[1]
        }
        for row in rows
    ]


@app.get("/api/severity")
def get_severity():

    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                severity,
                COUNT(*) AS total
            FROM alerts
            GROUP BY severity
            ORDER BY total DESC
        """)

        rows = cur.fetchall()

    conn.close()

    return [
        {
            "severity": row[0],
            "total": row[1]
        }
        for row in rows
    ]


@app.get("/api/events")
def get_events():

    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                id,
                timestamp,
                source_ip,
                destination_port,
                protocol,
                event_type,
                status,
                severity
            FROM events
            ORDER BY timestamp DESC
            LIMIT 20
        """)

        rows = cur.fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "timestamp": str(row[1]),
            "source_ip": str(row[2]),
            "destination_port": row[3],
            "protocol": row[4],
            "event_type": row[5],
            "status": row[6],
            "severity": row[7]
        }
        for row in rows
    ]

@app.get("/", response_class=HTMLResponse)
def dashboard():

    return """
<!DOCTYPE html>
<html>

<head>

<title>SIEM Security Dashboard</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #0b1120;
    color: #e2e8f0;
}

.container {
    padding: 30px;
}

.header {
    margin-bottom: 30px;
}

.header h1 {
    margin: 0;
}

.header p {
    color: #94a3b8;
}

.stats {
    display: grid;
    grid-template-columns:
        repeat(4, 1fr);

    gap: 20px;
}

.card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 20px;
}

.card-title {
    color: #94a3b8;
}

.card-number {
    font-size: 32px;
    font-weight: bold;
    margin-top: 10px;
}

.dashboard-grid {
    display: grid;
    grid-template-columns:
        1fr 1fr;

    gap: 20px;
    margin-top: 20px;
}

.panel {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 20px;
}

.panel h2 {
    margin-top: 0;
}

.bar {
    margin: 15px 0;
}

.bar-label {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
}

.bar-background {
    height: 10px;
    background: #1e293b;
    border-radius: 10px;
}

.bar-fill {
    height: 10px;
    border-radius: 10px;
    background: #38bdf8;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #1e293b;
}

th {
    color: #94a3b8;
}

.badge {
    padding: 5px 9px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: bold;
}

.CRITICAL {
    color: #ef4444;
}

.HIGH {
    color: #f97316;
}

.MEDIUM {
    color: #eab308;
}

.LOW {
    color: #22c55e;
}

.events {
    margin-top: 20px;
}

@media(max-width: 900px) {

    .stats {
        grid-template-columns:
            repeat(2, 1fr);
    }

    .dashboard-grid {
        grid-template-columns: 1fr;
    }

}

</style>

</head>


<body>

<div class="container">

<div class="header">

<h1>SIEM Security Dashboard</h1>

<p>
Autonomous Security Information and Event Management
</p>

</div>


<div class="stats">

<div class="card">

<div class="card-title">
Total Events
</div>

<div
    class="card-number"
    id="events">
-
</div>

</div>


<div class="card">

<div class="card-title">
Total Alerts
</div>

<div
    class="card-number"
    id="alerts">
-
</div>

</div>


<div class="card">

<div class="card-title">
Critical
</div>

<div
    class="card-number CRITICAL"
    id="critical">
-
</div>

</div>


<div class="card">

<div class="card-title">
High
</div>

<div
    class="card-number HIGH"
    id="high">
-
</div>

</div>

</div>


<div class="dashboard-grid">


<div class="panel">

<h2>Alert Severity</h2>

<div id="severity">
Loading...
</div>

</div>


<div class="panel">

<h2>K-Means Cluster</h2>

<div id="clusters">
Loading...
</div>

</div>


</div>


<div class="panel events">

<h2>Latest Security Events</h2>

<table>

<thead>

<tr>

<th>Time</th>
<th>Source IP</th>
<th>Port</th>
<th>Protocol</th>
<th>Event</th>
<th>Status</th>
<th>Severity</th>

</tr>

</thead>

<tbody id="eventTable">

</tbody>

</table>

</div>


<div class="panel events">

<h2>Top Anomalies</h2>

<table>

<thead>

<tr>

<th>Source IP</th>
<th>Score</th>
<th>Severity</th>
<th>Type</th>

</tr>

</thead>

<tbody id="alertTable">

</tbody>

</table>

</div>


</div>


<script>

async function getJSON(url) {

    const response = await fetch(url);

    return response.json();

}


async function loadDashboard() {

    const stats =
        await getJSON("/api/stats");


    document.getElementById("events")
        .textContent = stats.events;

    document.getElementById("alerts")
        .textContent = stats.alerts;

    document.getElementById("critical")
        .textContent = stats.critical;

    document.getElementById("high")
        .textContent = stats.high;


    const severity =
        await getJSON("/api/severity");


    const severityContainer =
        document.getElementById("severity");

    severityContainer.innerHTML = "";


    const maxSeverity =
        Math.max(
            ...severity.map(
                item => item.total
            ),
            1
        );


    severity.forEach(item => {

        const percentage =
            (item.total / maxSeverity) * 100;


        severityContainer.innerHTML += `

        <div class="bar">

            <div class="bar-label">

                <span class="${item.severity}">
                    ${item.severity}
                </span>

                <span>
                    ${item.total}
                </span>

            </div>

            <div class="bar-background">

                <div
                    class="bar-fill"
                    style="width:${percentage}%">
                </div>

            </div>

        </div>

        `;

    });


    const clusters =
        await getJSON("/api/clusters");


    const clusterContainer =
        document.getElementById("clusters");

    clusterContainer.innerHTML = "";


    const maxCluster =
        Math.max(
            ...clusters.map(
                item => item.total
            ),
            1
        );


    clusters.forEach(item => {

        const percentage =
            (item.total / maxCluster) * 100;


        clusterContainer.innerHTML += `

        <div class="bar">

            <div class="bar-label">

                <span>
                    Cluster ${item.cluster}
                </span>

                <span>
                    ${item.total}
                </span>

            </div>

            <div class="bar-background">

                <div
                    class="bar-fill"
                    style="width:${percentage}%">
                </div>

            </div>

        </div>

        `;

    });


    const events =
        await getJSON("/api/events");


    const eventTable =
        document.getElementById("eventTable");

    eventTable.innerHTML = "";


    events.forEach(event => {

        eventTable.innerHTML += `

        <tr>

            <td>
                ${event.timestamp}
            </td>

            <td>
                ${event.source_ip}
            </td>

            <td>
                ${event.destination_port}
            </td>

            <td>
                ${event.protocol}
            </td>

            <td>
                ${event.event_type}
            </td>

            <td>
                ${event.status}
            </td>

            <td class="${event.severity}">
                ${event.severity}
            </td>

        </tr>

        `;

    });


    const alerts =
        await getJSON("/api/alerts");


    const alertTable =
        document.getElementById("alertTable");

    alertTable.innerHTML = "";


    alerts.forEach(alert => {

        alertTable.innerHTML += `

        <tr>

            <td>
                ${alert.source_ip}
            </td>

            <td>
                ${alert.anomaly_score}
            </td>

            <td class="${alert.severity}">
                ${alert.severity}
            </td>

            <td>
                ${alert.alert_type}
            </td>

        </tr>

        `;

    });

}


loadDashboard();


setInterval(
    loadDashboard,
    5000
);

</script>

</body>

</html>
"""