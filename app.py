from flask import Flask, request, jsonify, redirect
import sqlite3
import string
import random

app = Flask(__name__)

DATABASE = "urls.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_code TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            clicks INTEGER DEFAULT 0
        )
    """)

    connection.commit()
    connection.close()


def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


@app.route("/")
def home():
    return "URL Shortener API is running!"


@app.route("/api/shorten", methods=["POST"])
def shorten_url():

    data = request.get_json()

    if not data or "url" not in data:
        return jsonify({
            "error": "URL is required"
        }), 400

    original_url = data["url"]

    connection = get_db_connection()

    short_code = generate_short_code()

    while connection.execute(
        "SELECT id FROM urls WHERE short_code = ?",
        (short_code,)
    ).fetchone():

        short_code = generate_short_code()

    connection.execute(
        """
        INSERT INTO urls (original_url, short_code)
        VALUES (?, ?)
        """,
        (original_url, short_code)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "original_url": original_url,
        "short_code": short_code,
        "short_url": f"http://127.0.0.1:5000/{short_code}"
    }), 201
@app.route("/<short_code>")
def redirect_to_url(short_code):

    connection = get_db_connection()

    url = connection.execute(
        "SELECT original_url FROM urls WHERE short_code = ?",
        (short_code,)
    ).fetchone()

    if url is None:
        connection.close()

        return jsonify({
            "error": "Short URL not found"
        }), 404

    connection.execute(
        "UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?",
        (short_code,)
    )

    connection.commit()
    connection.close()

    return redirect(url["original_url"])


if __name__ == "__main__":
    init_db()
    app.run(debug=True)