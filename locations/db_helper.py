import json
import logging
import os

import mariadb

logger = logging.getLogger(__name__)

SAMPLE_LOCATIONS = [
    (
        1,
        "CapitalTwo Main Street",
        "branch",
        "100 Main Street",
        "Example City",
        "CA",
        "00001",
        ["checking", "savings", "loans"],
    ),
    (
        2,
        "CapitalTwo Market Street ATM",
        "atm",
        "200 Market Street",
        "Example City",
        "CA",
        "00002",
        ["cash_withdrawal", "balance_inquiry"],
    ),
    (
        3,
        "CapitalTwo Oak Avenue",
        "branch",
        "300 Oak Avenue",
        "Sampletown",
        "CA",
        "00003",
        ["checking", "savings"],
    ),
]


def get_db_connection():
    try:
        return mariadb.connect(
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWD"],
            host=os.environ["DB_HOST"],
            port=int(os.getenv("DB_PORT", "3306")),
            database=os.environ["DB_NAME"],
        )
    except (KeyError, ValueError, mariadb.Error):
        logger.exception("Unable to connect to MariaDB")
        raise


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS locations (
                id INT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(50) NOT NULL,
                address VARCHAR(255) NOT NULL,
                city VARCHAR(100) NOT NULL,
                state VARCHAR(50) NOT NULL,
                postal_code VARCHAR(20) NOT NULL,
                services TEXT NOT NULL
            )
            """
        )
        cur.executemany(
            """
            INSERT IGNORE INTO locations
                (id, name, type, address, city, state, postal_code, services)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (*location[:7], json.dumps(location[7]))
                for location in SAMPLE_LOCATIONS
            ],
        )
        conn.commit()
        logger.info("Locations database schema verified")
    except mariadb.Error:
        conn.rollback()
        logger.exception("Unable to initialize locations database")
        raise
    finally:
        cur.close()
        conn.close()
