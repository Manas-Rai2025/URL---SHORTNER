from flask import Flask, render_template, request, jsonify, redirect
import sqlite3
import string
import random
import os

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

    print("===================================")
    print("SHORTEN REQUEST RECEIVED")
    print("===================================")

    data = request.get_json(silent=True)

    print("Received data:", data)

    if not data or "url" not in data:
        return jsonify({
            "error": "URL is required"
        }), 400

    original_url = data["url"].strip()

    print("Original URL:", original_url)

    if not original_url.startswith(("http://", "https://")):
        return jsonify({
            "error": "Invalid URL. URL must start with http:// or https://"
        }), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Generate unique short code
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
    # Use Render's public URL when deployed
    base_url = os.environ.get("RENDER_EXTERNAL_URL")

    if not base_url:
        base_url = request.host_url.rstrip("/")

    base_url = base_url.rstrip("/")

    short_url = base_url + "/" + short_code

    print("Base URL:", base_url)
    print("Short code:", short_code)
    print("FINAL SHORT URL:", short_url)

    return jsonify({
        "short_url": short_url
    }), 200


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


init_db()


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )