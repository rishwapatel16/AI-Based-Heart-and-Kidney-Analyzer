import sqlite3

def create_tables():

    conn = sqlite3.connect("health.db")
    cursor = conn.cursor()

    #  USERS TABLE (IMPORTANT)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password BLOB,
        city TEXT,
        profession TEXT
    )
    """)

    # PREDICTIONS TABLE (UPDATED)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        heart_result TEXT,
        kidney_result TEXT,
        final_result TEXT,
        heart_percent REAL,
        kidney_percent REAL,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()