import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join('data', 'users.db')

def init_db():
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_user(name, email):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users(name, email, created_at) VALUES (?, ?, ?)",
                    (name, email, datetime.utcnow().isoformat()))
        conn.commit()
        return True
    except Exception as e:
        # Could log e
        return False
    finally:
        conn.close()

def list_users():
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, created_at FROM users ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows
