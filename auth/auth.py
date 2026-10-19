from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import check_password_hash
from db_helper import get_db_connection
import mariadb

app = Flask(__name__)
CORS(app)

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    # Ensure necessary fields are present
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
        # Query the users password hash
        cur.execute("SELECT passwd FROM users WHERE uname = ?", (username,))
        result = cur.fetchone()

        # Check if password hash matches provided password
        if result and check_password_hash(result[0], password):
            return jsonify({"message": "Login successful"}), 200

        return jsonify({"message": "Invalid credentials"}), 401

    except mariadb.Error as e:
        app.logger.error(f"Error during authentication: {e}")
        return jsonify({"message": "Internal server error"}), 500
    finally:
        cur.close()
        conn.close()

# Debug mode if run directly
if __name__ == "__main__":
    app.run(debug=True)