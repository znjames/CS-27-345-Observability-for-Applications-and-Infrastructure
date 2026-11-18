from db_helper import get_db_connection
import mariadb


def record_transaction(username, tx_type, amount):
    """Returns 'ok', 'insufficient_funds', 'not_found', or 'error'."""
    conn = get_db_connection()
    if not conn:
        return "error"
    cur = conn.cursor()
    try:
        
        cur.execute(
            "SELECT id, balance FROM users WHERE uname = ? FOR UPDATE",
            (username,),
        )
        row = cur.fetchone()
        if row is None:
            conn.rollback()
            return "not_found"

        user_id, balance = row
        new_balance = balance + amount if tx_type == "deposit" else balance - amount

        if new_balance < 0:
            conn.rollback()
            return "insufficient_funds"

        cur.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, user_id))
        cur.execute(
            "INSERT INTO transactions (user_id, type, amount, balance_after) "
            "VALUES (?, ?, ?, ?)",
            (user_id, tx_type, amount, new_balance),
        )
        conn.commit()
        return "ok"
    except mariadb.Error as e:
        print(f"Transaction error: {e}")
        conn.rollback()
        return "error"
    finally:
        cur.close()
        conn.close()


def get_transaction_history(username, limit=50):
    conn = get_db_connection()
    if not conn:
        return []
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT t.type, t.amount, t.balance_after, t.created_at "
            "FROM transactions t JOIN users u ON u.id = t.user_id "
            "WHERE u.uname = ? "
            "ORDER BY t.created_at DESC, t.id DESC LIMIT ?",
            (username, limit),
        )
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()