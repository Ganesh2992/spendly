# Spec: Login and Logout

## Overview

This feature implements session-based authentication in the Spendly expense tracker. The `/login` form (`templates/login.html`) and `/logout` route both exist as placeholders — `/login` only handles GET and `/logout` returns a plain string. This step wires them up: on POST, `/login` validates credentials against the `users` table using `werkzeug.security.check_password_hash`, establishes a server-side session via Flask's `session`, and redirects authenticated users to `/profile`. `/logout` clears the session and redirects to `/`. With this step done, every subsequent placeholder (`/profile`, `/expenses/add`, etc.) can rely on `session["user_id"]` being present for any logged-in user.

## Depends on

- Step 1 — Database setup (`users` table must exist with `email` and `password_hash` columns)
- Step 2 — Registration (`users` must be populated with real rows so login can succeed; the `demo@spendly.com` / `demo123` account from `seed_db()` is a good first credential to test against)

## Routes

- POST `/login` — Process login form, verify email + password, set `session["user_id"]`, redirect to `/profile` on success or re-render form with error on failure — public
- GET `/login` — (already exists) Renders the login form — public
- GET `/logout` — Clear `session`, redirect to `/` with a flash message — public (idempotent — logging out when not logged in just redirects)

## Database changes

No database changes — the `users` table from Step 1 is sufficient. Required columns already exist: `email`, `password_hash`.

## Templates

- Creates: None
- Modify: `templates/login.html` — Add `value="{{ email or '' }}"` to the email input so it repopulates after a failed login (mirrors what `register.html` already does for name/email). Form already posts to `/login` and `action` is correct.

## Files to change

- `app.py` — Add POST handling to `/login` (validate input, look up user by email, verify password with `check_password_hash`, set `session["user_id"]`, redirect to `/profile` or re-render with flash). Rewrite `/logout` placeholder to clear the session and redirect to `/`. Import `session` from `flask` and `check_password_hash` from `werkzeug.security`.
- `templates/login.html` — Preserve email value on re-render (small edit, mirrors `register.html` pattern).

## Files to create

None

## New dependencies

No new dependencies. Uses:
- `flask.session` (Flask stdlib, already a dependency via `flask` itself)
- `werkzeug.security.check_password_hash` (Werkzeug is already installed — `generate_password_hash` is already used in `app.py` and `database/db.py`)
- `get_db()` from `database/db.py` (already imported)
- `flash`, `redirect`, `render_template`, `request`, `url_for` (already imported)

## Rules for implementation

- No SQLAlchemy or ORMs — use raw SQL via `get_db()`
- Parameterised queries only — never use string formatting in SQL
- Passwords must be verified with `werkzeug.security.check_password_hash` (never compare hashes or plaintext directly)
- All flash messages and error styling must use CSS variables — never hardcode hex values in inline styles
- All templates must extend `base.html` (already satisfied — `login.html` extends `base.html`)
- Email handling: `.strip().lower()` before lookup, so `Demo@Spendly.com` and `demo@spendly.com` are treated as the same account
- After verifying the password, store the user's `id` in `session["user_id"]` (integer). Do not store the email or password hash in the session
- On successful login: flash a success message (e.g. "Signed in successfully.") and redirect to `/profile` (the Step 4 placeholder, which is fine — even if the page is still a string stub, the redirect itself is the spec target)
- On failed login: use a single, deliberately vague error message ("Invalid email or password") to avoid leaking whether the email exists — this is a defensive-security default; do not differentiate "email not found" from "wrong password" to the user
- On `/logout`: `session.clear()` (or pop `session["user_id"]`), flash "Signed out successfully." (info or success category), redirect to `/`. `/logout` should be safe to hit when already logged out — no error if the session is empty
- Always close the `get_db()` connection after the lookup (mirror the `try/except/finally` pattern already used in `/register`)
- Don't add a "remember me" checkbox or long-lived tokens in this step — plain session cookie is enough for the learning-project scope. If the user wants persistence beyond the browser session, they can extend it later
- Do not introduce a `current_user` decorator or helper in this step — keep the change minimal. Subsequent steps (profile, expenses) can read `session.get("user_id")` directly or build a small helper as part of their own spec
- Form field names must match what's already in `templates/login.html`: `email`, `password`

## Definition of done

- [ ] GET `/login` continues to render the form as before
- [ ] POST `/login` with a valid email + correct password sets `session["user_id"]`, flashes a success message, and redirects to `/profile`
- [ ] POST `/login` with an unknown email does not set a session and re-renders the form with a single vague error
- [ ] POST `/login` with a known email but wrong password does not set a session and re-renders the form with the same vague error
- [ ] POST `/login` with empty email or empty password re-renders the form with a validation error and does not query the database
- [ ] Email lookup is case-insensitive and whitespace-trimmed (`  Demo@Spendly.com  ` works the same as `demo@spendly.com`)
- [ ] After a failed login, the email field is repopulated with the user's input
- [ ] After successful login, hitting `/login` again should redirect to `/profile` (a logged-in user has no business on the login form)
- [ ] GET `/logout` clears the session and redirects to `/` with a flash message
- [ ] GET `/logout` is safe to call when not logged in (no traceback, just a redirect)
- [ ] Password hashes are never compared directly or sent to the template — only `check_password_hash` is used
- [ ] All SQL uses parameterised statements
- [ ] No new pip packages are added
- [ ] No new files are created
- [ ] App starts without errors
- [ ] Can verify end-to-end by running `python app.py`, signing in as `demo@spendly.com` / `demo123` (seeded by Step 1), seeing the redirect to `/profile`, clicking logout, and landing back on `/`
