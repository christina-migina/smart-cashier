import sqlite3
import config


def get_connection():
    return sqlite3.connect(config.DATABASE_PATH)

def execute_query(connection, sql, params=()):
    cursor = connection.cursor()
    cursor.execute(sql, params)
    connection.commit()

def fetch_query(connection, sql, params=()):
    cursor = connection.cursor()
    cursor.execute(sql, params)
    return cursor.fetchall()

def init_db():
    connection = get_connection()
    sql = """
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        features BLOB NOT NULL
        )"""
    execute_query(connection, sql)
    connection.close()

def add_item_to_db(name, price, features_array):
    connection = get_connection()
    sql = "INSERT INTO items (name, price, features) VALUES (?, ?, ?)"

    features = features_array.tobytes()
    params = (name, price, features)

    execute_query(connection, sql, params)
    connection.close()

def get_all_items():
    connection = get_connection()
    sql = "SELECT name, price, features FROM items"
    items = fetch_query(connection, sql)
    connection.close()
    return items