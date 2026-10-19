# Configure mariadb on startup
def on_starting(server):
    from db_helper import init_db
    init_db()