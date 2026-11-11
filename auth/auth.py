from flask import Flask, jsonify, request
from werkzeug.security import check_password_hash
from db_helper import get_db_connection
import mariadb
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "supersecretkey"

jwt = JWTManager(app)

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
            access_token = create_access_token(identity=username)

            return jsonify({
                "message": "Login successful",
                "access_token": access_token
            }), 200

        return jsonify({"message": "Invalid credentials"}), 401

    except mariadb.Error as e:
        app.logger.error(f"Error during authentication: {e}")
        return jsonify({"message": "Internal server error"}), 500
    finally:
        cur.close()
        conn.close()


@app.route("/api/auth/balance", methods=["GET"])
@jwt_required()
def get_balance():

    username = get_jwt_identity()

    conn = get_db_connection()
    if not conn:
        return jsonify({"message": "Database error"}), 500

    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT balance FROM users WHERE uname = ?",
            (username,)
        )

        result = cur.fetchone()

        if not result:
            return jsonify({"message": "User not found"}), 404

        return jsonify({
            "balance": float(result[0])
        }), 200

    except mariadb.Error as e:
        app.logger.error(f"Balance error: {e}")
        return jsonify({"message": "Internal server error"}), 500

    finally:
        cur.close()
        conn.close()


@app.route("/api/auth/deposit", methods=["POST"])
@jwt_required()
def deposit():
    username = get_jwt_identity()
    amount = request.json.get("amount")

    if not amount or amount <= 0:
        return jsonify({"message": "Invalid amount"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET balance = balance + ? WHERE uname = ?",
        (amount, username)
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Deposit successful!"}), 200


@app.route("/api/auth/withdraw", methods=["POST"])
@jwt_required()
def withdraw():
    username = get_jwt_identity()
    amount = request.json.get("amount")

    if not amount or amount <= 0:
        return jsonify({"message": "Invalid amount"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET balance = balance - ? WHERE uname = ? AND balance >= ?",
        (amount, username, amount)
    )

    if cur.rowcount == 0:
        cur.close()
        conn.close()
        return jsonify({"message": "Insufficient funds"}), 400

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Withdrawal successful!"}), 200

# Debug mode if run directly
if __name__ == "__main__":
    app.run(debug=True)