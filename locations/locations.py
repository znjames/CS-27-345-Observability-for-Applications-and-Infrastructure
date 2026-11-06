import json

import mariadb
from flask import Flask, jsonify

from db_helper import get_db_connection

app = Flask(__name__)


@app.get("/healthz")
def health_check():
    return jsonify({"status": "ok"}), 200


@app.get("/api/locations")
def list_locations():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT id, name, type, address, city, state, postal_code, services
            FROM locations
            ORDER BY id
            """
        )
        locations = [
            {
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "address": row[3],
                "city": row[4],
                "state": row[5],
                "postal_code": row[6],
                "services": json.loads(row[7]),
            }
            for row in cur.fetchall()
        ]
        return jsonify({"locations": locations}), 200
    except mariadb.Error:
        app.logger.exception("Unable to retrieve locations")
        return jsonify({"message": "Internal server error"}), 500
    finally:
        cur.close()
        conn.close()


@app.get("/api/locations/<int:location_id>")
def get_location(location_id):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT id, name, type, address, city, state, postal_code, services
            FROM locations
            WHERE id = ?
            """,
            (location_id,),
        )
        row = cur.fetchone()
        if row is None:
            return jsonify({"message": "Location not found"}), 404

        return jsonify(
            {
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "address": row[3],
                "city": row[4],
                "state": row[5],
                "postal_code": row[6],
                "services": json.loads(row[7]),
            }
        ), 200
    except mariadb.Error:
        app.logger.exception("Unable to retrieve location %s", location_id)
        return jsonify({"message": "Internal server error"}), 500
    finally:
        cur.close()
        conn.close()
