import sqlite3
from datetime import date, timedelta
from pathlib import Path

from werkzeug.security import generate_password_hash

# Project root = parent of the database/ package. Resolving from __file__
# keeps the path stable regardless of the working directory `python app.py`
# is launched from.
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "expense_tracker.db"


def get_db():
    """Open a SQLite connection with dict-like rows and FK enforcement on."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables if they don't exist. Safe to call multiple times."""
    conn = get_db()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                email         TEXT    UNIQUE NOT NULL,
                password_hash TEXT    NOT NULL,
                created_at    TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id),
                amount      REAL    NOT NULL,
                category    TEXT    NOT NULL,
                date        TEXT    NOT NULL,
                description TEXT,
                created_at  TEXT    DEFAULT (datetime('now'))
            );
            """
        )
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def seed_db():
    """Insert demo user + 8 sample expenses. No-op if data already exists."""
    conn = get_db()
    try:
        existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if existing > 0:
            return

        conn.execute(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
        )
        demo_user_id = conn.execute(
            "SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)
        ).fetchone()["id"]

        today = date.today()
        sample_expenses = [
            (demo_user_id, 80.0,   "Food",          today - timedelta(days=20), "Morning chai and biscuit"),
            (demo_user_id, 450.0,  "Food",          today - timedelta(days=15), "Weekly groceries"),
            (demo_user_id, 220.0,  "Transport",     today - timedelta(days=12), "Uber to office"),
            (demo_user_id, 1500.0, "Bills",         today - timedelta(days=10), "Electricity bill"),
            (demo_user_id, 650.0,  "Health",        today - timedelta(days=8),  "Pharmacy restock"),
            (demo_user_id, 399.0,  "Entertainment", today - timedelta(days=5),  "Movie ticket"),
            (demo_user_id, 1299.0, "Shopping",      today - timedelta(days=3),  "T-shirt"),
            (demo_user_id, 150.0,  "Other",         today - timedelta(days=1),  "Miscellaneous"),
        ]

        conn.executemany(
            """
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            sample_expenses,
        )

        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()

