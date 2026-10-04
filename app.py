from flask import Flask, render_template, request, jsonify, redirect
import sqlite3
import string
import secrets

app = Flask(__name__)

DATABASE = "urls.db"


def generate_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def get_connection():
    return sqlite3.connect(DATABASE)


def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_code TEXT UNIQUE NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json()

    if not data or "url" not in data:
        return jsonify({"error": "URL is required"}), 400

    original_url = data["url"].strip()

    if not original_url.startswith(("http://", "https://")):
        return jsonify({"error": "Invalid URL"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    while True:
        short_code = generate_code()

        cursor.execute(
            "SELECT id FROM urls WHERE short_code = ?",
            (short_code,)
        )

        if cursor.fetchone() is None:
            break

    cursor.execute(
        "INSERT INTO urls (original_url, short_code) VALUES (?, ?)",
        (original_url, short_code)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "short_url": request.host_url + short_code
    })


@app.route("/<short_code>")
def redirect_url(short_code):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT original_url FROM urls WHERE short_code = ?",
        (short_code,)
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        return redirect(result[0])

    return "Short URL not found", 404


create_table()


if __name__ == "__main__":
    app.run(debug=True)