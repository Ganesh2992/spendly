"""One-off script: insert a single dummy Indian user into expense_tracker.db."""
import random
import sys
from pathlib import Path

# Make `database` importable when run from project root
sys.path.insert(0, str(Path(__file__).resolve().parent))

from werkzeug.security import generate_password_hash

from database.db import get_db, init_db


# Realistic Indian first + last names spanning regions.
# Tuples are (first_name, last_name) — keep names plausible together.
INDIAN_NAMES = [
    # North
    ("Rahul", "Sharma"), ("Priya", "Verma"), ("Amit", "Gupta"),
    ("Neha", "Agarwal"), ("Vikas", "Mishra"), ("Pooja", "Saxena"),
    ("Rohit", "Singh"), ("Anjali", "Pandey"),
    # South
    ("Arjun", "Iyer"), ("Divya", "Nair"), ("Karthik", "Rao"),
    ("Meera", "Krishnan"), ("Vijay", "Reddy"), ("Lakshmi", "Pillai"),
    # East
    ("Sourav", "Banerjee"), ("Rina", "Das"), ("Arijit", "Chatterjee"),
    ("Sneha", "Mukherjee"), ("Rajesh", "Sahoo"),
    # West
    ("Hardik", "Patel"), ("Nisha", "Shah"), ("Karan", "Mehta"),
    ("Riya", "Joshi"), ("Sandeep", "Deshmukh"), ("Aishwarya", "Kulkarni"),
    # Central / misc
    ("Vivek", "Tiwari"), ("Ananya", "Chauhan"), ("Saurabh", "Dubey"),
    ("Kavita", "Yadav"), ("Manish", "Thakur"),
]


def email_for(first: str, last: str) -> str:
    """Lowercased first.last + 2–3 digit suffix @gmail.com."""
    suffix = random.randint(10, 999)
    return f"{first.lower()}.{last.lower()}{suffix}@gmail.com"


def pick_unique_email(conn) -> tuple[str, str, str]:
    """Keep drawing (first, last, suffix) until the email is unused."""
    for _ in range(500):
        first, last = random.choice(INDIAN_NAMES)
        email = email_for(first, last)
        taken = conn.execute(
            "SELECT 1 FROM users WHERE email = ?", (email,)
        ).fetchone()
        if not taken:
            return first, last, email
    raise RuntimeError("Could not generate a unique email after 500 tries")


def main() -> None:
    # Ensure tables exist (no-op if already created).
    init_db()

    conn = get_db()
    try:
        first, last, email = pick_unique_email(conn)
        name = f"{first} {last}"
        password_hash = generate_password_hash("password123")

        cur = conn.execute(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (name, email, password_hash),
        )
        conn.commit()
        user_id = cur.lastrowid

        print("Dummy user created successfully!")
        print(f"  id:    {user_id}")
        print(f"  name:  {name}")
        print(f"  email: {email}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
