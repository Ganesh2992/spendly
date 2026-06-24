# Spec: Registration

## Overview

This feature implements the backend logic for user registration in the Spendly expense tracker. The landing page links to `/register`, and the registration form (`templates/register.html`) already exists and posts to `/register`, but the route currently only handles GET requests and just renders the form. This step adds POST handling: validating input, hashing the password, inserting the new user into the `users` table, and redirecting to the login page on success or re-rendering the form with an error message on failure. This is the first authentication-related step in the roadmap and enables the login step (Step 3) to follow.

## Depends on

- Step 1 — Database setup (`users` table must exist with `name`, `email`, `password_hash` columns)

## Routes

- POST `/register` — Process registration form, validate input, insert new user, redirect to `/login` on success or re-render form with error on failure — public
- GET `/register` — (already exists) Renders the registration form — public

## Database changes

No database changes — the `users` table from Step 1 is sufficient. Required columns already exist: `name`, `email` (unique), `password_hash`, `created_at`.

## Templates

- Creates: None
- Modify: None (the form template already exists and has the correct structure)

## Files to change

- `app.py` — Update `/register` route to handle POST requests, add validation, password hashing, and user insertion logic

## Files to create

None

## New dependencies

No new dependencies. Uses:
- `werkzeug.security.generate_password_hash` (already installed and used in `database/db.py`)
- `sqlite3` (standard library, already used via `get_db()`)
- `flask.request`, `flask.redirect`, `flask.url_for`, `flask.flash` (or equivalent error passing)

## Rules for implementation

- No SQLAlchemy or ORMs — use raw SQL via the `get_db()` function
- Parameterised queries only — never use string formatting in SQL
- Passwords must be hashed with `werkzeug.security.generate_password_hash`
- All flash messages and error styling must use CSS variables — never hardcode hex values in inline styles
- All templates must extend `base.html` (already satisfied — `register.html` extends `base.html`)
- Email validation: check format (contains `@` and `.`) and uniqueness
- Password validation: minimum 8 characters
- Name validation: not empty, stripped of whitespace
- On successful registration: redirect to `/login` with a success message
- On validation failure or duplicate email: re-render `/register` form with error message
- Use `flash()` for success messages and pass `error` variable to template for form errors (or use `flash()` for both — choose one approach and be consistent)
- Handle `sqlite3.IntegrityError` specifically for duplicate email scenarios
- All database operations must use the existing `get_db()` function from `database/db.py`
- Connection management: close the database connection after use (or use context manager pattern)
- Form field names must match what's already in `templates/register.html`: `name`, `email`, `password`

## Definition of done

- [ ] POST request to `/register` with valid name, email, and password (≥8 chars) creates a new user in the database
- [ ] Password is stored as a hash, not plaintext
- [ ] POST request with duplicate email shows an error message and does not create a user
- [ ] POST request with invalid email format shows an error message
- [ ] POST request with password < 8 characters shows an error message
- [ ] POST request with empty name shows an error message
- [ ] GET request to `/register` continues to render the form as before
- [ ] Successful registration redirects to `/login` (or shows success message)
- [ ] Failed registration re-renders the form with the error visible
- [ ] All SQL queries use parameterised statements
- [ ] No new files are created
- [ ] No new pip packages are added
- [ ] App starts without errors
- [ ] Can verify by running `python app.py` and submitting the registration form
