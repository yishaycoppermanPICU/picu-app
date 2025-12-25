import sqlite3
from datetime import datetime
import os

DB_DIR = 'data'
DB_PATH = os.path.join(DB_DIR, 'users.db')

def init_db():
    """
    Initialize or migrate the users database.
    Ensures the users table exists and contains columns:
    id, name, email, uid, provider, photo_url, created_at, last_login
    Safe to run multiple times.
    """
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create table if not exists with a full schema (id, name, email, uid, provider, photo_url, created_at, last_login)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        uid TEXT UNIQUE,
        provider TEXT,
        photo_url TEXT,
        created_at TEXT,
        last_login TEXT
    )
    """)
    conn.commit()

    # Migration: ensure older DBs get missing columns (SQLite supports ADD COLUMN)
    cur.execute("PRAGMA table_info(users)")
    cols = [r[1] for r in cur.fetchall()]

    for col_def in [
        ("uid", "TEXT"),
        ("provider", "TEXT"),
        ("photo_url", "TEXT"),
        ("created_at", "TEXT"),
        ("last_login", "TEXT")
    ]:
        col_name, col_type = col_def
        if col_name not in cols:
            try:
                cur.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            except Exception:
                # ignore if cannot add (already present or incompatible)
                pass

    conn.commit()
    conn.close()

def add_user(name, email):
    """
    Simple legacy user add (used by the quick signup form).
    Stores created_at as UTC ISO timestamp.
    Returns True on success, False on failure.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users(name, email, created_at) VALUES (?, ?, ?)",
                    (name, email, datetime.utcnow().isoformat()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # likely UNIQUE constraint on email
        return False
    except Exception:
        return False
    finally:
        conn.close()

def add_or_update_google_user(uid, name, email, photo_url=None):
    """
    Add a new user or update an existing one based on uid OR email.
    Records provider='google' and updates last_login timestamp.
    Returns True on success, False on failure.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    try:
        # Try find by uid first; if uid empty, match by email
        if uid:
            cur.execute("SELECT id FROM users WHERE uid = ?", (uid,))
            row = cur.fetchone()
        else:
            row = None

        if not row:
            # fallback: find by email
            cur.execute("SELECT id FROM users WHERE email = ?", (email,))
            row = cur.fetchone()

        if row:
            # update existing
            cur.execute("""UPDATE users
                           SET name = ?, email = ?, photo_url = ?, provider = ?, last_login = ?
                           WHERE id = ?""",
                        (name, email, photo_url, 'google', now, row[0]))
        else:
            # insert new
            cur.execute("""INSERT INTO users(name, email, uid, provider, photo_url, created_at, last_login)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (name, email, uid, 'google', photo_url, now, now))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # try to recover from unique constraint conflicts by updating the email row
        try:
            cur.execute("SELECT id FROM users WHERE email = ?", (email,))
            row2 = cur.fetchone()
            if row2:
                cur.execute("""UPDATE users
                               SET name = ?, photo_url = ?, provider = ?, uid = ?, last_login = ?
                               WHERE id = ?""",
                            (name, photo_url, 'google', uid, now, row2[0]))
                conn.commit()
                return True
        except Exception:
            pass
        return False
    except Exception:
        return False
    finally:
        conn.close()

def list_users():
    """
    Return users as a list of tuples:
    (id, name, email, created_at, uid, provider, photo_url, last_login)
    Ordered by created_at desc (if available).
    """
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, email, created_at, uid, provider, photo_url, last_login FROM users ORDER BY created_at DESC")
        rows = cur.fetchall()
    except Exception:
        rows = []
    finally:
        conn.close()
    return rows
