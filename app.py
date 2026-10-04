from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import string
import random

app = Flask(__name__)

DATABASE = "urls.db"


def generate_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


def init_db():
    conn = sqlite3.connect(DATABASE)
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
        return jsonify({
            "error": "URL is required"
        }), 400

    original_url = data["url"].strip()

    if not original_url.startswith(("http://", "https://")):
        return jsonify({
            "error": "Invalid URL. URL must start with http:// or https://"
        }), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Generate a unique short code
    while True:
        short_code = generate_code()

        cursor.execute(
            "SELECT id FROM urls WHERE short_code = ?",
            (short_code,)
        )

        if cursor.fetchone() is None:
            break

    # Save URL
    cursor.execute(
        """
        INSERT INTO urls (original_url, short_code)
        VALUES (?, ?)
        """,
        (original_url, short_code)
    )

    conn.commit()
    conn.close()

    # IMPORTANT:
    # Generate the URL using the current deployed domain
    short_url = url_for(
        "redirect_url",
        short_code=short_code,
        _external=True
    )

    return jsonify({
        "short_url": short_url
    })


@app.route("/<short_code>")
def redirect_url(short_code):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT original_url
        FROM urls
        WHERE short_code = ?
        """,
        (short_code,)
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return redirect(result[0])

    return "Short URL not found", 404


# Initialize database when application starts
init_db()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )