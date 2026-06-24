import re
import sqlite3

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import get_db, init_db, seed_db

app = Flask(__name__)
# Dev-only secret key for session/flash support. Replace with env var in production.
app.secret_key = "dev-secret-key-change-in-production"

# Initialize and seed the database on startup. Idempotent — safe to run
# on every boot (CREATE TABLE IF NOT EXISTS + seed_db's COUNT(*) guard).
with app.app_context():
    init_db()
    seed_db()


# --- Mock data for /profile (Step 4 — replaced in Step 5) --- #
# Step 4 is UI-first per specs/04-profile.md. These dicts/lists are the
# source of truth for the profile page until Step 5 wires up real queries
# against the users/expenses tables.
MOCK_USER = {
    "initials": "DU",
    "name": "Demo User",
    "email": "demo@spendly.com",
    "member_since": "March 2024",
}

MOCK_STATS = {
    "total_spent": 12450.0,
    "transaction_count": 27,
    "top_category": "Food",
    "avg_per_transaction": 461.11,
}

# (date, description, category, amount, badge_tone)
MOCK_TRANSACTIONS = [
    ("2026-06-23", "Morning chai and biscuit",  "Food",           80.0,  "food"),
    ("2026-06-21", "T-shirt",                   "Shopping",     1299.0,  "shopping"),
    ("2026-06-19", "Movie ticket",              "Entertainment", 399.0,  "entertainment"),
    ("2026-06-16", "Pharmacy restock",          "Health",        650.0,  "health"),
    ("2026-06-14", "Electricity bill",          "Bills",        1500.0,  "bills"),
    ("2026-06-12", "Uber to office",            "Transport",     220.0,  "transport"),
    ("2026-06-09", "Weekly groceries",          "Food",          450.0,  "food"),
    ("2026-06-04", "Miscellaneous",             "Other",         150.0,  "other"),
]

# (name, total, percent, badge_tone)
MOCK_CATEGORIES = [
    ("Food",           3030.0, 24, "food"),
    ("Bills",          2800.0, 22, "bills"),
    ("Shopping",       2100.0, 17, "shopping"),
    ("Transport",      1550.0, 12, "transport"),
    ("Health",         1200.0, 10, "health"),
    ("Entertainment",   870.0,  7, "entertainment"),
    ("Other",           900.0,  7, "other"),
]


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Validate name
        if not name:
            flash("Name is required", "error")
            return render_template("register.html", name=name, email=email)

        # Validate email
        if not email:
            flash("Email is required", "error")
            return render_template("register.html", name=name, email=email)

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash("Invalid email format", "error")
            return render_template("register.html", name=name, email=email)

        # Validate password
        if len(password) < 8:
            flash("Password must be at least 8 characters", "error")
            return render_template("register.html", name=name, email=email)

        # Insert user
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password)),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
            flash("Email already registered. Please sign in instead.", "error")
            return render_template("register.html", name=name, email=email)
        finally:
            conn.close()

        flash("Account created successfully! Please sign in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        # Preserve the user's input (not the lowercased form) in the re-render
        # so the field reflects what they actually typed.
        email_display = request.form.get("email", "").strip()

        if not email or not password:
            flash("Please enter both email and password.", "error")
            return render_template("login.html", email=email_display)

        conn = get_db()
        try:
            user = conn.execute(
                "SELECT id, password_hash FROM users WHERE email = ?",
                (email,),
            ).fetchone()
        finally:
            conn.close()

        if not user or not check_password_hash(user["password_hash"], password):
            # Single vague error — don't leak whether the email exists.
            flash("Invalid email or password", "error")
            return render_template("login.html", email=email_display)

        session["user_id"] = user["id"]
        flash("Signed in successfully.", "success")
        return redirect(url_for("profile"))

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    flash("Signed out successfully.", "success")
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    # Auth guard. The first route in the project that requires a session —
    # kept inline so Steps 7–9 can adopt the same shape. Promote to a
    # helper or decorator only when the duplication actually hurts.
    if not session.get("user_id"):
        flash("Please sign in to view your profile.", "error")
        return redirect(url_for("login"))

    # Step 4 is UI-first per specs/04-profile.md — all data is hardcoded
    # in the MOCK_* constants above. Step 5 replaces this with real DB
    # queries against the users/expenses tables.
    return render_template(
        "profile.html",
        current_user_name=MOCK_USER["name"],
        user=MOCK_USER,
        stats=MOCK_STATS,
        transactions=MOCK_TRANSACTIONS,
        categories=MOCK_CATEGORIES,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
