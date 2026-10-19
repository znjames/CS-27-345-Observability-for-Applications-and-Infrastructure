from werkzeug.security import check_password_hash
import mariadb

# Returns a mariadb connection object using preconfigured connection parameters
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

# Initializes necessary tables if they don't exist
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