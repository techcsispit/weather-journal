"""SQLite storage module for weather history."""

import sqlite3
from datetime import datetime
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "weather_journal.db"


def get_connection(db_path=DEFAULT_DB_PATH):
    """Establishes connection to the SQLite database and ensures table exists."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            temp REAL NOT NULL,
            humidity INTEGER,
            condition TEXT,
            logged_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def save_entry(city, temp, humidity, condition, logged_at=None, db_path=DEFAULT_DB_PATH):
    """Saves a weather observation record to the database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    ts = logged_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO entries (city, temp, humidity, condition, logged_at)
        VALUES (?, ?, ?, ?, ?)
    """, (city, temp, humidity, condition, ts))
    conn.commit()
    conn.close()


def get_history(city=None, db_path=DEFAULT_DB_PATH):
    """Retrieves logged weather records."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    if not city:
        cursor.execute("SELECT city, temp, humidity, condition, logged_at FROM entries ORDER BY id DESC")
    else:
        cursor.execute("SELECT city, temp, humidity, condition, logged_at FROM entries WHERE LOWER(city) = LOWER(?) ORDER BY id DESC", (city,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
