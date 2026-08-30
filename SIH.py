from flask import Flask, request, redirect, url_for, session, render_template_string
import os
import sqlite3
from datetime import datetime

# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

# Use an environment variable on Render if available
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "smart-inspection-secure-key-2026"
)

DATABASE = "inspection.db"


# ============================================================
# DATABASE
# ============================================================

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'Inspector'
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS inspections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            inspector TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            priority TEXT DEFAULT 'Normal',
            date TEXT
        )
    """)

    # Demo login
    existing_user = connection.execute(
        "SELECT * FROM users WHERE username = ?",
        ("admin",)
    ).fetchone()

    if existing_user is None:
        connection.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", "admin123", "Administrator")
        )

    # Demo inspection data
    count = connection.execute(
        "SELECT COUNT(*) AS total FROM inspections"
    ).fetchone()["total"]

    if count == 0:
        demo_data = [
            ("Government Hostel - Raipur", "Inspector 01", "Completed", "High"),
            ("NGO Centre - Bhilai", "Inspector 02", "Pending", "Normal"),
            ("Skill Development Centre", "Inspector 03", "In Progress", "High"),
            ("Welfare Institution - Durg", "Inspector 04", "Pending", "Low")
        ]

        for location, inspector, status, priority in demo_data:
            connection.execute(
                """
                INSERT INTO inspections
                (location, inspector, status, priority, date)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    location,
                    inspector,
                    status,
                    priority,
                    datetime.now().strftime("%Y-%m-%d")
                )
            )

    connection.commit()
    connection.close()


# ============================================================
# HOME PAGE
# ============================================================

HOME_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>Smart Monitoring & Inspection System</title>

    <style>

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: Arial, Helvetica, sans-serif;
            background: #f2f6ff;
            color: #1f2937;
        }

        /* ==================================================
           NAVBAR
        ================================================== */

        .navbar {
            height: 58px;
            background: linear-gradient(
                90deg,
                #111827,
                #173d91,
                #2459d6
            );

            display: flex;
            align-items: center;
            justify-content: space-between;

            padding: 0 7%;

            color: white;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 10px;

            font-size: 17px;
            font-weight: bold;
        }

        .brand-icon {
            font-size: 20px;
        }

        .login-link {
            color: white;
            text-decoration: none;

            font-size: 17px;
            font-weight: bold;

            padding: 10px 15px;
            border-radius: 7px;

            transition: 0.3s;
        }

        .login-link:hover {
            background: rgba(255,255,255,0.15);
        }


        /* ==================================================
           HERO
        ================================================== */

        .hero {
            text-align: center;

            padding: 105px 20px 70px;
        }

        .hero h1 {
            color: #23478e;

            font-size: 43px;

            margin-bottom: 25px;

            font-weight: 700;
        }

        .hero p {
            font-size: 18px;

            color: #303846;

            margin-bottom: 30px;
        }

        .main-button {
            display: inline-block;

            background: #2867df;

            color: white;

            text-decoration: none;

            padding: 13px 23px;

            border-radius: 7px;

            font-size: 15px;

            font-weight: 600;

            box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25);

            transition: 0.3s;
        }

        .main-button:hover {
            background: #1e4fb4;

            transform: translateY(-2px);
        }


        /* ==================================================
           FEATURE CARDS
        ================================================== */

        .features {
            width: 76%;

            margin: 20px auto 90px;

            display: grid;

            grid-template-columns:
                repeat(4, 1fr);

            gap: 18px;
        }

        .feature-card {
            background: white;

            min-height: 185px;

            border-radius: 15px;

            padding: 38px 23px;

            box-shadow:
                0 5px 18px rgba(0,0,0,0.08);

            transition: 0.3s;
        }

        .feature-card:hover {
            transform: translateY(-5px);

            box-shadow:
                0 10px 25px rgba(0,0,0,0.12);
        }

        .feature-title {
            color: #294a88;

            font-size: 20px;

            margin-bottom: 18px;

            font-weight: bold;
        }

        .feature-icon {
            margin-right: 8px;
        }

        .feature-card p {
            font-size: 16px;

            line-height: 1.35;

            color: #30343b;
        }


        /* ==================================================
           LOGIN PAGE
        ================================================== */

        .login-container {
            width: 100%;

            min-height: calc(100vh - 58px);

            display: flex;

            align-items: center;

            justify-content: center;

            padding: 30px;
        }

        .login-box {
            width: 400px;

            background: white;

            padding: 40px;

            border-radius: 15px;

            box-shadow:
                0 8px 30px rgba(0,0,0,0.10);
        }

        .login-box h2 {
            text-align: center;

            color: #23478e;

            margin-bottom: 10px;
        }

        .login-box .subtitle {
            text-align: center;

            color: #666;

            margin-bottom: 28px;
        }

        .form-group {
            margin-bottom: 18px;
        }

        .form-group label {
            display: block;

            margin-bottom: 7px;

            font-weight: 600;
        }

        .form-group input {
            width: 100%;

            padding: 12px;

            border: 1px solid #ccd3df;

            border-radius: 7px;

            font-size: 15px;

            outline: none;
        }

        .form-group input:focus {
            border-color: #2867df;

            box-shadow:
                0 0 0 3px rgba(40,103,223,0.12);
        }

        .login-button {
            width: 100%;

            padding: 13px;

            background: #2867df;

            color: white;

            border: none;

            border-radius: 7px;

            font-size: 16px;

            font-weight: bold;

            cursor: pointer;
        }

        .login-button:hover {
            background: #1e4fb4;
        }

        .error {
            background: #fee2e2;

            color: #b91c1c;

            padding: 10px;

            border-radius: 6px;

            margin-bottom: 18px;

            text-align: center;
        }

        .demo-login {
            margin-top: 20px;

            padding: 12px;

            background: #eef4ff;

            border-radius: 7px;

            font-size: 13px;

            color: #345;
        }


        /* ==================================================
           DASHBOARD
        ================================================== */

        .dashboard {
            padding: 35px 6%;
        }

        .dashboard-header {
            display: flex;

            justify-content: space-between;

            align-items: center;

            margin-bottom: 30px;
        }

        .dashboard-header h1 {
            color: #23478e;
        }

        .logout-button {
            text-decoration: none;

            color: white;

            background: #dc3545;

            padding: 10px 18px;

            border-radius: 7px;
        }

        .stats {
            display: grid;

            grid-template-columns:
                repeat(4, 1fr);

            gap: 18px;

            margin-bottom: 30px;
        }

        .stat-card {
            background: white;

            border-radius: 12px;

            padding: 22px;

            box-shadow:
                0 5px 18px rgba(0,0,0,0.07);
        }

        .stat-card h3 {
            color: #555;

            font-size: 15px;

            margin-bottom: 10px;
        }

        .stat-number {
            font-size: 30px;

            color: #2459d6;

            font-weight: bold;
        }

        .inspection-section {
            background: white;

            border-radius: 13px;

            padding: 25px;

            box-shadow:
                0 5px 18px rgba(0,0,0,0.07);
        }

        .inspection-section h2 {
            color: #23478e;

            margin-bottom: 20px;
        }

        .inspection-table {
            width: 100%;

            border-collapse: collapse;
        }

        .inspection-table th,
        .inspection-table td {
            padding: 14px;

            border-bottom: 1px solid #e5e7eb;

            text-align: left;
        }

        .inspection-table th {
            background: #f1f5ff;

            color: #23478e;
        }

        .status {
            padding: 5px 10px;

            border-radius: 15px;

            font-size: 13px;
        }

        .completed {
            background: #dcfce7;

            color: #15803d;
        }

        .pending {
            background: #fef3c7;

            color: #a16207;
        }

        .progress {
            background: #dbeafe;

            color: #1d4ed8;
        }

        .high {
            color: #dc2626;

            font-weight: bold;
        }

        .normal {
            color: #2563eb;

            font-weight: bold;
        }

        .low {
            color: #16a34a;

            font-weight: bold;
        }


        /* ==================================================
           MOBILE
        ================================================== */

        @media (max-width: 900px) {

            .features {
                width: 90%;

                grid-template-columns:
                    repeat(2, 1fr);
            }

            .stats {
                grid-template-columns:
                    repeat(2, 1fr);
            }

            .hero h1 {
                font-size: 34px;
            }
        }

        @media (max-width: 600px) {

            .navbar {
                padding: 0 20px;
            }

            .brand {
                font-size: 14px;
            }

            .features {
                grid-template-columns: 1fr;
            }

            .stats {
                grid-template-columns: 1fr;
            }

            .hero {
                padding-top: 70px;
            }

            .hero h1 {
                font-size: 29px;
            }

            .hero p {
                font-size: 16px;
            }

            .login-box {
                width: 100%;
            }

            .inspection-section {
                overflow-x: auto;
            }

            .inspection-table {
                min-width: 650px;
            }
        }

    </style>
</head>

<body>

    <!-- NAVBAR -->

    <nav class="navbar">

        <div class="brand">
            <span class="brand-icon">🏛️</span>
            Smart Monitoring & Inspection System
        </div>

        <a href="{{ url_for('login') }}"
           class="login-link">
            🔐 Login
        </a>

    </nav>


    <!-- HERO -->

    <section class="hero">

        <h1>
            Smart Real-Time Monitoring & Inspection System
        </h1>

        <p>
            A digital platform for field inspection,
            evidence collection and real-time issue monitoring.
        </p>

        <a href="{{ url_for('login') }}"
           class="main-button">
            🔐 Login to System
        </a>

    </section>


    <!-- FEATURES -->

    <section class="features">

        <div class="feature-card">

            <div class="feature-title">
                <span class="feature-icon">👷</span>
                Field Inspection
            </div>

            <p>
                Workers and Inspectors conduct inspections
                directly from assigned locations.
            </p>

        </div>


        <div class="feature-card">

            <div class="feature-title">
                <span class="feature-icon">📷</span>
                Evidence Capture
            </div>

            <p>
                Upload photographic evidence together
                with inspection reports.
            </p>

        </div>


        <div class="feature-card">

            <div class="feature-title">
                <span class="feature-icon">📍</span>
                GPS Location
            </div>

            <p>
                Capture the location of field inspections
                and associate it with inspection reports.
            </p>

        </div>


        <div class="feature-card">

            <div class="feature-title">
                <span class="feature-icon">🤖</span>
                Smart Priority
            </div>

            <p>
                Repeated problems automatically receive
                higher inspection priority.
            </p>

        </div>

    </section>

</body>
</html>
"""


# ============================================================
# LOGIN PAGE
# ============================================================

LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>Login - Smart Inspection</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;

            font-family: Arial, Helvetica, sans-serif;

            background: #f2f6ff;
        }

        .navbar {
            height: 58px;

            background: linear-gradient(
                90deg,
                #111827,
                #173d91,
                #2459d6
            );

            display: flex;

            align-items: center;

            justify-content: space-between;

            padding: 0 7%;

            color: white;
        }

        .brand {
            font-weight: bold;
        }

        .home {
            color: white;

            text-decoration: none;
        }

        .container {
            min-height: calc(100vh - 58px);

            display: flex;

            align-items: center;

            justify-content: center;

            padding: 20px;
        }

        .box {
            width: 400px;

            background: white;

            padding: 40px;

            border-radius: 15px;

            box-shadow:
                0 8px 30px rgba(0,0,0,0.1);
        }

        h1 {
            text-align: center;

            color: #23478e;

            margin-bottom: 8px;
        }

        .subtitle {
            text-align: center;

            color: #666;

            margin-bottom: 30px;
        }

        label {
            display: block;

            margin-bottom: 7px;

            font-weight: bold;
        }

        input {
            width: 100%;

            padding: 12px;

            margin-bottom: 18px;

            border: 1px solid #ccd3df;

            border-radius: 7px;

            font-size: 15px;
        }

        button {
            width: 100%;

            padding: 13px;

            background: #2867df;

            color: white;

            border: none;

            border-radius: 7px;

            font-size: 16px;

            font-weight: bold;

            cursor: pointer;
        }

        button:hover {
            background: #1e4fb4;
        }

        .error {
            background: #fee2e2;

            color: #b91c1c;

            padding: 10px;

            border-radius: 6px;

            text-align: center;

            margin-bottom: 18px;
        }

        .demo {
            background: #eef4ff;

            margin-top: 20px;

            padding: 12px;

            border-radius: 7px;

            font-size: 13px;
        }

    </style>

</head>

<body>

<nav class="navbar">

    <div class="brand">
        🏛️ Smart Monitoring & Inspection System
    </div>

    <a href="{{ url_for('home') }}"
       class="home">
        Home
    </a>

</nav>


<div class="container">

    <div class="box">

        <h1>🔐 Login</h1>

        <p class="subtitle">
            Access the Inspection Management System
        </p>


        {% if error %}

        <div class="error">
            {{ error }}
        </div>

        {% endif %}


        <form method="POST">

            <label>Username</label>

            <input
                type="text"
                name="username"
                placeholder="Enter username"
                required
            >


            <label>Password</label>

            <input
                type="password"
                name="password"
                placeholder="Enter password"
                required
            >


            <button type="submit">
                Login
            </button>

        </form>


        <div class="demo">

            <strong>Demo Login</strong><br><br>

            Username: <b>admin</b><br>

            Password: <b>admin123</b>

        </div>

    </div>

</div>

</body>
</html>
"""


# ============================================================
# DASHBOARD
# ============================================================

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>Dashboard - Smart Inspection</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;

            font-family: Arial, Helvetica, sans-serif;

            background: #f2f6ff;

            color: #222;
        }

        .navbar {
            height: 58px;

            background: linear-gradient(
                90deg,
                #111827,
                #173d91,
                #2459d6
            );

            display: flex;

            align-items: center;

            justify-content: space-between;

            padding: 0 6%;

            color: white;
        }

        .brand {
            font-weight: bold;
        }

        .logout {
            color: white;

            text-decoration: none;

            background: #dc3545;

            padding: 8px 15px;

            border-radius: 6px;
        }

        .dashboard {
            padding: 35px 6%;
        }

        .header {
            display: flex;

            justify-content: space-between;

            align-items: center;

            margin-bottom: 25px;
        }

        .header h1 {
            color: #23478e;
        }

        .stats {
            display: grid;

            grid-template-columns:
                repeat(4, 1fr);

            gap: 18px;

            margin-bottom: 30px;
        }

        .stat {
            background: white;

            padding: 23px;

            border-radius: 12px;

            box-shadow:
                0 5px 18px rgba(0,0,0,0.07);
        }

        .stat h3 {
            color: #666;

            font-size: 14px;
        }

        .number {
            font-size: 30px;

            color: #2459d6;

            font-weight: bold;
        }

        .section {
            background: white;

            padding: 25px;

            border-radius: 12px;

            box-shadow:
                0 5px 18px rgba(0,0,0,0.07);

            overflow-x: auto;
        }

        .section h2 {
            color: #23478e;

            margin-top: 0;
        }

        table {
            width: 100%;

            border-collapse: collapse;

            min-width: 650px;
        }

        th,
        td {
            padding: 13px;

            border-bottom: 1px solid #ddd;

            text-align: left;
        }

        th {
            background: #eef4ff;

            color: #23478e;
        }

        .badge {
            padding: 5px 10px;

            border-radius: 15px;

            font-size: 12px;
        }

        .completed {
            background: #dcfce7;

            color: #15803d;
        }

        .pending {
            background: #fef3c7;

            color: #a16207;
        }

        .progress {
            background: #dbeafe;

            color: #1d4ed8;
        }

        .high {
            color: #dc2626;

            font-weight: bold;
        }

        .normal {
            color: #2563eb;

            font-weight: bold;
        }

        .low {
            color: #16a34a;

            font-weight: bold;
        }

        @media(max-width:800px) {

            .stats {
                grid-template-columns:
                    repeat(2, 1fr);
            }

        }

        @media(max-width:500px) {

            .stats {
                grid-template-columns: 1fr;
            }

            .dashboard {
                padding: 25px 4%;
            }

            .header {
                display: block;
            }

            .header h1 {
                font-size: 25px;
            }

        }

    </style>

</head>

<body>

<nav class="navbar">

    <div class="brand">
        🏛️ Smart Monitoring & Inspection System
    </div>

    <a href="{{ url_for('logout') }}"
       class="logout">
        Logout
    </a>

</nav>


<main class="dashboard">

    <div class="header">

        <div>

            <h1>Monitoring Dashboard</h1>

            <p>
                Welcome, {{ username }} 👋
            </p>

        </div>

    </div>


    <!-- STATISTICS -->

    <div class="stats">

        <div class="stat">

            <h3>Total Inspections</h3>

            <div class="number">
                {{ total }}
            </div>

        </div>


        <div class="stat">

            <h3>Completed</h3>

            <div class="number">
                {{ completed }}
            </div>

        </div>


        <div class="stat">

            <h3>Pending</h3>

            <div class="number">
                {{ pending }}
            </div>

        </div>


        <div class="stat">

            <h3>High Priority</h3>

            <div class="number">
                {{ high_priority }}
            </div>

        </div>

    </div>


    <!-- INSPECTIONS -->

    <div class="section">

        <h2>📋 Recent Inspections</h2>

        <table>

            <thead>

                <tr>

                    <th>ID</th>

                    <th>Location</th>

                    <th>Inspector</th>

                    <th>Status</th>

                    <th>Priority</th>

                    <th>Date</th>

                </tr>

            </thead>

            <tbody>

                {% for item in inspections %}

                <tr>

                    <td>{{ item["id"] }}</td>

                    <td>{{ item["location"] }}</td>

                    <td>{{ item["inspector"] }}</td>

                    <td>

                        {% if item["status"] == "Completed" %}

                        <span class="badge completed">
                            Completed
                        </span>

                        {% elif item["status"] == "Pending" %}

                        <span class="badge pending">
                            Pending
                        </span>

                        {% else %}

                        <span class="badge progress">
                            In Progress
                        </span>

                        {% endif %}

                    </td>

                    <td class="{{ item['priority'].lower() }}">
                        {{ item["priority"] }}
                    </td>

                    <td>{{ item["date"] }}</td>

                </tr>

                {% endfor %}

            </tbody>

        </table>

    </div>

</main>

</body>

</html>
"""


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def home():
    return render_template_string(HOME_PAGE)


@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        connection = get_db()

        user = connection.execute(
            """
            SELECT * FROM users
            WHERE username = ? AND password = ?
            """,
            (username, password)
        ).fetchone()

        connection.close()

        if user:

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            return redirect(url_for("dashboard"))

        error = "Invalid username or password."

    return render_template_string(
        LOGIN_PAGE,
        error=error
    )


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db()

    inspections = connection.execute(
        """
        SELECT * FROM inspections
        ORDER BY id DESC
        """
    ).fetchall()

    total = len(inspections)

    completed = sum(
        1 for x in inspections
        if x["status"] == "Completed"
    )

    pending = sum(
        1 for x in inspections
        if x["status"] == "Pending"
    )

    high_priority = sum(
        1 for x in inspections
        if x["priority"] == "High"
    )

    connection.close()

    return render_template_string(
        DASHBOARD_PAGE,
        inspections=inspections,
        total=total,
        completed=completed,
        pending=pending,
        high_priority=high_priority,
        username=session.get("username")
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ============================================================
# APPLICATION START
# ============================================================

initialize_database()


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
