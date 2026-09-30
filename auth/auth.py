import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
import mariadb
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
CORS(app)


def get_db_connection():
    try:
        conn = mariadb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWD"),
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            database=os.getenv("DB_NAME"),
        )
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None


def init_db():
    conn = get_db_connection()
    if not conn:
        print("Could not connect to database on startup.")
        sys.exit(1)

    cur = conn.cursor()

    try:
        # Create users table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                uname VARCHAR(255) NOT NULL UNIQUE,
                passwd VARCHAR(255) NOT NULL
            )
        """
        )

        # Hash default admin password before saving
        admin_pass_hash = generate_password_hash("admin")

        # Insert default admin user if not already present
        cur.execute(
            "INSERT IGNORE INTO users (uname, passwd) VALUES (?, ?)",
            ("admin", admin_pass_hash),
        )
        conn.commit()
        print("Database schema verified.")
    except mariadb.Error as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


# Run DB initialization when starting the app
init_db()


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or "uname" not in data or "passwd" not in data:
        return jsonify({"message": "Missing username or password"}), 400

    username = data.get("uname")
    password = data.get("passwd")

    # Start database connection
    conn = get_db_connection()
    if not conn:
        return jsonify({"message": "Database error"}), 500

    cur = conn.cursor()

    try:
        # Query user password hash using parameterized query to prevent SQL Injection
        cur.execute("SELECT passwd FROM users WHERE uname = ?", (username,))
        result = cur.fetchone()

        if result and check_password_hash(result[0], password):
            # Login successful
            return jsonify({"message": "Login successful"}), 200

        return jsonify({"message": "Invalid credentials"}), 401

    except mariadb.Error as e:
        app.logger.error(f"Error during authentication: {e}")
        return jsonify({"message": "Internal server error"}), 500
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)