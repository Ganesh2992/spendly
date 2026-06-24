import re
import sqlite3

from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from database.db import get_db, init_db, seed_db

app = Flask(__name__)
# Dev-only secret key for session/flash support. Replace with env var in production.
app.secret_key = "dev-secret-key-change-in-production"

# Initialize and seed the database on startup. Idempotent — safe to run
# on every boot (CREATE TABLE IF NOT EXISTS + seed_db's COUNT(*) guard).
with app.app_context():
    init_db()
    seed_db()


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


@app.route("/login")
def login():
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
    return "Logout — coming in Step 3"


@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


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
