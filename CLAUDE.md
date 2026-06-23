# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Spendly** is a personal expense tracking web app (rupee-denominated, Indian context) built as a learning project. It's a Flask app in its early stages — most authenticated/CRUD features are placeholder routes that students are expected to implement step-by-step. The landing page, register/login pages, terms, and privacy policy are already built.

## Commands

The project uses a local Python virtual environment (`venv/` is already created).

```bash
# Activate venv (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install/refresh dependencies
pip install -r requirements.txt

# Run the dev server (debug mode, port 5001)
python app.py

# Run tests
pytest

# Run a single test file
pytest tests/test_specific.py

# Run a single test by name
pytest -k "test_name_substring"
```

Dev server: http://localhost:5001

## Architecture

```
expense-tracker/
├── app.py                    # Flask app, all routes live here
├── database/
│   ├── __init__.py
│   └── db.py                 # SQLite helpers (TO BE IMPLEMENTED in Step 1)
├── templates/                # Jinja2 templates extending base.html
│   ├── base.html             # Layout: navbar, footer, loads style.css + main.js
│   ├── landing.html          # Hero + features + CTA + YouTube demo modal
│   ├── register.html
│   ├── login.html
│   ├── terms.html
│   └── privacy.html
├── static/
│   ├── css/style.css         # Global theme (DM Serif Display + DM Sans)
│   └── js/main.js            # Vanilla JS: modal open/close + YouTube iframe control
├── tests/                    # (not yet present — will be added)
├── requirements.txt          # flask, werkzeug, pytest, pytest-flask
└── venv/                     # Local virtual environment
```

### Key design decisions

- **Single-file Flask app**: `app.py` contains all routes. No blueprints, no app factory. The dev server is launched with `app.run(debug=True, port=5001)` directly.
- **SQLite via `database/db.py`**: This file is currently a stub. It must implement `get_db()` (returns connection with `row_factory` set to `sqlite3.Row` and `PRAGMA foreign_keys = ON`), `init_db()` (creates tables with `CREATE TABLE IF NOT EXISTS`), and `seed_db()` (sample data for development). The DB file is `expense_tracker.db` (gitignored).
- **Vanilla JS only** — no frameworks, no npm. `main.js` uses a data-attribute pattern: any element with `data-modal-open="<id>"` opens the matching modal; elements with `data-modal-close` close their parent `.modal`. YouTube embeds are lazy-loaded — `src` is set only on first open, and cleared on close to stop playback.
- **Single global stylesheet**: `static/css/style.css` is loaded by `base.html`. All styling lives there. Brand uses serif (`DM Serif Display`) for headings, sans (`DM Sans`) for body.
- **Base template provides**: navbar (brand + Sign in / Get started), footer (brand + Terms + Privacy links), and the main content block. All pages extend it.

### Implementation roadmap (visible from placeholder routes in `app.py`)

The placeholder routes in `app.py` map to a numbered build sequence. Follow this order when adding features — each step assumes the prior ones are done:

| Step | Route                                | Status        |
|------|--------------------------------------|---------------|
| 1    | `database/db.py` (get_db/init/seed)  | stub          |
| 3    | `/logout`                            | placeholder   |
| 4    | `/profile`                           | placeholder   |
| 7    | `/expenses/add`                      | placeholder   |
| 8    | `/expenses/<id>/edit`                | placeholder   |
| 9    | `/expenses/<id>/delete`              | placeholder   |

Authentication routes (`/register`, `/login`) and the static marketing/legal pages are already complete.

## Conventions

- **Commits**: Use Conventional Commits style with a scope prefix matching the area touched — e.g. `landing: ...`, `db: ...`, `auth: ...`, `expenses: ...`. Look at `git log` for the established pattern.
- **Scope of changes**: When a task says "modify only X," do not touch other files even if related. The recent commit history shows a pattern of tightly-scoped, single-purpose commits.
- **No JS framework**: Don't add npm packages, React, jQuery, etc. The project is explicitly vanilla.
- **Indian rupee (₹)**: Currency symbol and "rupee" wording are intentional — this is an Indian-market app. Keep amounts in ₹, not $.
- **DB file location**: `expense_tracker.db` at project root, created at runtime, gitignored.



// CampusX Claude.md



<!-- Project overview
Spendly is a lightweight personal expense tracker built with Flask and SQLite.

Architecture
spendly/
├── app.py              # All routes — single file, no blueprints
├── database/
│   └── db.py           # SQLite helpers: get_db(), init_db(), seed_db()
├── templates/
│   ├── base.html       # Shared layout — all templates must extend this
│   └── *.html          # One template per page
├── static/
│   ├── css/
│   │   ├── style.css       # Global styles
│   │   └── landing.css     # Landing-page-only styles
│   └── js/
│       └── main.js         # Vanilla JS only
└── requirements.txt
Where things belong:

New routes → app.py only, no blueprints
DB logic → database/db.py only, never inline in routes
New pages → new .html file extending base.html
Page-specific styles → new .css file, not inline <style> tags
Code style
Python: PEP 8, snake_case for all variables and functions
Templates: Jinja2 with url_for() for every internal link — never hardcode URLs
Route functions: one responsibility only — fetch data, render template, done
DB queries: always use parameterized queries (? placeholders) — never f-strings in SQL
Error handling: use abort() for HTTP errors, not bare return "error string"
Tech constraints
Flask only — no FastAPI, no Django, no other web frameworks
SQLite only — no PostgreSQL, no SQLAlchemy ORM, no external DB
Vanilla JS only — no React, no jQuery, no npm packages
No new pip packages — work within requirements.txt as-is unless explicitly told otherwise
Python 3.10+ assumed — f-strings and match statements are fine
Subagent Policy
Always use a builtin explore subagent for codebase exploration before implementing any new feature
Always use a subagent to verify test results after any implementation
When asked to plan, delegate codebase research to a subagent before presenting the plan
always use a builtin plan subagent in plan mode
Commands
# Setup
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run dev server (port 5001)
python app.py

# Run all tests
pytest

# Run a specific test file
pytest tests/test_foo.py

# Run a specific test by name
pytest -k "test_name"

# Run tests with output visible
pytest -s
Implemented vs stub routes
Route	Status
GET /	Implemented — renders landing.html
GET /register	Implemented — renders register.html
GET /login	Implemented — renders login.html
GET /logout	Stub — Step 3
GET /profile	Stub — Step 4
GET /expenses/add	Stub — Step 7
GET /expenses/<id>/edit	Stub — Step 8
GET /expenses/<id>/delete	Stub — Step 9
Do not implement a stub route unless the active task explicitly targets that step.

Warnings and things to avoid
Never use raw string returns for stub routes once a step is implemented — always render a template
Never hardcode URLs in templates — always use url_for()
Never put DB logic in route functions — it belongs in database/db.py
Never install new packages mid-feature without flagging it — keep requirements.txt in sync
Never use JS frameworks — the frontend is intentionally vanilla
database/db.py is currently empty — do not assume helpers exist until the step that implements them
FK enforcement is manual — SQLite foreign keys are off by default; get_db() must run PRAGMA foreign_keys = ON on every connection
The app runs on port 5001, not the Flask default 5000 — don't change this -->