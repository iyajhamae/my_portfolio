
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "iya-portfolio-secret-key"

DATABASE = Path(__file__).parent / "portfolio.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    projects = [
        (
            "Pixel Sprout",
            "A creative project showcasing visual design and digital creativity.",
            "Creative Design · Figma"
        ),
        (
            "SmartMed",
            "A digital design project focused on presenting a healthcare-related concept.",
            "UI/UX Design · Figma"
        ),
        (
            "Vintage Spirits",
            "A design project exploring a vintage-inspired visual identity and aesthetic.",
            "Graphic Design · Figma"
        ),
        (
            "Cafe Belgravia",
            "A café-themed design project featuring an elegant and inviting visual direction.",
            "UI/UX Design · Figma"
        ),
        (
            "Readrada",
            "A reading-related digital design project focused on presenting a concept for readers.",
            "UI/UX Design · Figma"
        ),
        (
            "SALAYSAY",
            "A web-based multimedia platform presenting Philippine folktales and cultural stories through digital storytelling, illustration, animation, audio narration, and interactive features.",
            "UI/UX Design · Multimedia"
        )
    ]

    # Update existing projects or insert new ones
    for title, description, category in projects:
        connection.execute("""
            INSERT INTO projects (title, description, category)
            VALUES (?, ?, ?)
            ON CONFLICT DO NOTHING
        """, (title, description, category))

        connection.execute("""
            UPDATE projects
            SET description = ?, category = ?
            WHERE title = ?
        """, (description, category, title))

    connection.commit()
    connection.close()


@app.route("/")
def home():
    connection = get_db_connection()

    projects = connection.execute("""
        SELECT * FROM projects
        WHERE title IN (
            'Pixel Sprout',
            'SmartMed',
            'Vintage Spirits',
            'Cafe Belgravia',
            'Readrada',
            'SALAYSAY'
        )
        ORDER BY CASE title
            WHEN 'Pixel Sprout' THEN 1
            WHEN 'SmartMed' THEN 2
            WHEN 'Vintage Spirits' THEN 3
            WHEN 'Cafe Belgravia' THEN 4
            WHEN 'Readrada' THEN 5
            WHEN 'SALAYSAY' THEN 6
        END
    """).fetchall()

    connection.close()

    return render_template("index.html", projects=projects)


@app.route("/send-message", methods=["POST"])
def send_message():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not email or not message:
        flash("Please complete all the fields.", "error")
        return redirect(url_for("home") + "#contact")

    if len(name) > 100 or len(email) > 254 or len(message) > 3000:
        flash("One or more fields are too long.", "error")
        return redirect(url_for("home") + "#contact")

    connection = get_db_connection()

    connection.execute("""
        INSERT INTO messages (name, email, message)
        VALUES (?, ?, ?)
    """, (name, email, message))

    connection.commit()
    connection.close()

    flash("Thank you! Your message has been received.", "success")

    return redirect(url_for("home") + "#contact")


initialize_database()


if __name__ == "__main__":
    app.run(debug=True)
