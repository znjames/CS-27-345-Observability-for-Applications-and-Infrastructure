from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from flask import Flask, jsonify, request
from werkzeug.security import check_password_hash
from db_helper import get_db_connection
import mariadb
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from transaction.transactions import record_transaction, get_transaction_history


app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "supersecretkey"

jwt = JWTManager(app)


def parse_amount(value):
    try:
        amount = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        return None
    return amount if amount > 0 else None


@app.route("/api/auth/login", methods=["POST"])
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
    data = request.get_json(silent=True) or {}
    amount = parse_amount(data.get("amount"))

    if amount is None:
        return jsonify({"message": "Invalid amount"}), 400

    result = record_transaction(username, "deposit", amount)
    if result == "ok":
        return jsonify({"message": "Deposit successful!"}), 200
    if result == "not_found":
        return jsonify({"message": "User not found"}), 404
    return jsonify({"message": "Internal server error"}), 500


@app.route("/api/auth/withdraw", methods=["POST"])
@jwt_required()
def withdraw():
    username = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    amount = parse_amount(data.get("amount"))

    if amount is None:
        return jsonify({"message": "Invalid amount"}), 400

    result = record_transaction(username, "withdraw", amount)
    if result == "ok":
        return jsonify({"message": "Withdrawal successful!"}), 200
    if result == "insufficient_funds":
        return jsonify({"message": "Insufficient funds"}), 400
    if result == "not_found":
        return jsonify({"message": "User not found"}), 404
    return jsonify({"message": "Internal server error"}), 500


@app.route("/api/auth/transactions", methods=["GET"])
@jwt_required()
def transactions():
    username = get_jwt_identity()
    rows = get_transaction_history(username, limit=50)
    return jsonify([
        {
            "type": tx_type,
            "amount": str(amount),
            "balance_after": str(balance_after),
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for tx_type, amount, balance_after, created_at in rows
    ])


# Debug mode if run directly
if __name__ == "__main__":
    app.run(debug=True)