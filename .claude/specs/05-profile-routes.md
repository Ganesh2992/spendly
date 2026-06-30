# Spec: Profile Routes

## Overview

This feature wires the `/profile` page (built in Step 4) to the real database. The current `app.py` route renders the template with hardcoded `MOCK_USER`, `MOCK_STATS`, `MOCK_TRANSACTIONS`, and `MOCK_CATEGORIES` constants. This step replaces those mocks with live SQL queries against the `users` and `expenses` tables, scoped to the logged-in user via `session["user_id"]`. It also adds a `?date_from=&date_to=` query-string filter (driven by the filter bar already present in `templates/profile.html`) so the page can show "This Month", "Last 3 Months", "All Time", and custom date ranges without a full re-render. After this step, `templates/profile.html` consumes only real data and the page is ready for Step 7 (add), Step 8 (edit), and Step 9 (delete) to fill in the table.

## Depends on

- Step 1 — Database setup (`users` and `expenses` tables must exist)
- Step 2 — Registration (`users` must be populated; `seed_db()` provides `demo@spendly.com` for development)
- Step 3 — Login + Logout (`session["user_id"]` must be set for the auth guard in `/profile`)
- Step 4 — Profile Page UI (`templates/profile.html` already references the real data shape: `user.*`, `stats.total/count/top_category`, `tx.{date, description, category, amount, id}`, `cat.{name, amount, percent}`, plus `presets`, `date_from`, `date_to`)

## Routes

- GET `/profile` — Query the `users` and `expenses` tables for the logged-in user, render the profile page with computed stats, recent transactions, and a category breakdown. Accepts optional `?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD` query params to filter expenses. When no filter is present, shows "All Time" (no date constraint). — logged-in only (redirect to `/login` if `session["user_id"]` is missing)

No new routes are created — `/profile` is the only one rewritten.

## Database changes

No database changes. The existing `users` and `expenses` tables from Step 1 are sufficient. Required columns already exist:

- `users`: `id`, `name`, `email`, `created_at` (used for `member_since` formatting)
- `expenses`: `id`, `user_id`, `amount`, `category`, `date`, `description` (used for the transaction table, the stats card, and the category breakdown)

## Templates

- Creates: None
- Modify: None in this step. `templates/profile.html` already exists from Step 4 and already references the real data shape. Do **not** edit it as part of Step 5 — the route's job is to match what the template expects, not the other way round.

## Files to change

- `app.py` — Rewrite the `/profile` route to:
  1. Keep the existing auth guard: if `session.get("user_id")` is missing, flash an error and redirect to `/login`.
  2. Look up the current user from the `users` table (single row by `id`).
  3. Parse optional `date_from` and `date_to` query params (validate as `YYYY-MM-DD`; silently ignore malformed values — fall back to "All Time").
  4. Query the `expenses` table for the current user, filtered by the date range when present, ordered by `date DESC` and then `id DESC` (most recent first).
  5. Compute the summary stats from the filtered expenses: `total` (sum of `amount`), `count` (number of rows), `top_category` (category with the largest sum, or `None`/`"—"` if no expenses).
  6. Compute the category breakdown: group expenses by `category`, sum the `amount` for each, compute each category's percent of the total, sort by amount descending.
  7. Build the four date-range presets (`this_month`, `last_3`, `last_6`, plus implicit "All Time") for the filter bar.
  8. Format `user.member_since` from `users.created_at` (e.g. `"March 2024"`).
  9. Compute `user.initials` from the user's name (first letter of the first two whitespace-separated words, uppercased — e.g. `"Demo User"` → `"DU"`, `"Ganesh"` → `"G"`, `"Anita Priya Sharma"` → `"AP"`).
  10. Remove the `MOCK_USER`, `MOCK_STATS`, `MOCK_TRANSACTIONS`, `MOCK_CATEGORIES` constants (no longer used) and the leading comment block that references Step 4 mocks.
  11. Render `profile.html` with the computed context variables matching the names already referenced in the template.

- `database/db.py` — No changes. (All data access happens via `get_db()`.)

## Files to create

None

## New dependencies

No new dependencies. Uses:
- `sqlite3` (standard library, already used via `get_db()`)
- `datetime.date` (standard library — for computing "this month", "last 3 months", "last 6 months" preset ranges and for validating/formatting dates)
- `flask.session`, `flask.flash`, `flask.redirect`, `flask.render_template`, `flask.request`, `flask.url_for` (already imported in `app.py`)

## Rules for implementation

- No SQLAlchemy or ORMs — use raw sqlite3 via `get_db()`
- Parameterised queries only — never use string formatting in SQL
- Passwords hashed with werkzeug (no changes to auth in this step)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html` (no new templates in this step)
- **Auth guard stays inline** — keep the `if not session.get("user_id"): ...` block at the top of `/profile` exactly as it is. Do not promote it to a decorator or helper in this step; Steps 7–9 will adopt the same inline shape and we can extract it later if duplication actually hurts.
- **Always close the connection** — wrap the `get_db()` call in a `try/finally` block (mirror the pattern in `/register` and `/login`) and call `conn.close()` in the `finally` block.
- **Single DB connection per request** — open `get_db()` once at the top of the route, run all queries against it, close it once at the end. Don't open a new connection per query.
- **Date filter semantics**:
  - When **neither** `date_from` nor `date_to` is present: no date clause in the SQL — show "All Time".
  - When **only `date_from`** is present: `WHERE date >= date_from`.
  - When **only `date_to`** is present: `WHERE date <= date_to`.
  - When **both** are present: `WHERE date >= date_from AND date <= date_from` (inclusive on both ends).
  - Malformed dates (not matching `^\d{4}-\d{2}-\d{2}$`) are silently dropped — treat the request as if the param was not sent. Do not flash an error.
  - If `date_from > date_to` (after parsing), still return an empty result set — do not flash an error.
- **Filter parameter names** — must match the `name` attributes in the template's `<input>`s: `date_from`, `date_to` (snake_case, not camelCase).
- **Preset values** — compute `date_from`/`date_to` for each preset using `date.today()` as the anchor. "This Month" = first day of current month → today. "Last 3 Months" = first day of (current month − 2) → today. "Last 6 Months" = first day of (current month − 5) → today. Always format as `YYYY-MM-DD` strings so they can be passed straight back into the URL.
- **Empty state** — when the filtered query returns zero rows:
  - `stats.total` = `0`, `stats.count` = `0`, `stats.top_category` = `None` (the template will show "—" via existing logic; if not, the route can pass an empty string — pick whichever the template expects and stick with it).
  - `expenses` = `[]` (the template already has a `{% if not expenses %}` branch that renders the "No expenses found for this period." row).
  - `categories` = `[]` (the template's `{% for cat in categories %}` will simply render nothing).
- **Stats**:
  - `total` is a float, sum of `amount` for the filtered rows. Format with two decimal places at render time (e.g. `₹{{ "%.2f" | format(stats.total) }}` or equivalent — the template already shows `₹{{ stats.total }}` so it's fine to pass a float and let Jinja's default formatting handle it; verify visually).
  - `count` is an integer.
  - `top_category` is the category with the highest total `amount` (alphabetical tiebreak if two categories sum to the same value); `None` if there are no expenses.
- **Category breakdown**:
  - Group by `category`, sum `amount`, compute `percent = (category_total / total) * 100` (rounded to the nearest integer).
  - Sort by `category_total` descending.
  - Each row shape (matching template): `{"name": "Food", "amount": 3030.0, "percent": 24}`.
  - **Edge case**: if the filtered total is `0` (no expenses in range), `percent` for every row would be a division by zero. Since `categories` is empty in that case, the loop never runs — no special handling needed. Just make sure the division is guarded if you ever decide to render anything for the empty case.
- **Ordering**:
  - Recent transactions: `ORDER BY date DESC, id DESC` (most recent first; `id` as tiebreaker so same-day rows are deterministic).
  - Category breakdown: by total descending (most-spent first), then alphabetical.
- **Transactions row shape** (must match the template's `tx.*` references): `{"id": int, "date": "YYYY-MM-DD", "description": str | None, "category": str, "amount": float}`.
- **User dict shape** (must match `user.*` references): `{"name": str, "email": str, "initials": str, "member_since": "Month YYYY"}`.
- **Current user greeting** — `base.html` reads `current_user_name` from the template context to render "Hello, {name}" in the navbar. Pass `current_user_name=user["name"]` (or just `current_user_name=name` if you hoist the name into a local variable). Do not break the navbar.
- **Currency formatting** — the template shows `₹{{ stats.total }}` and `₹{{ tx.amount }}`. The `₹` symbol is in the template; the route just passes the numeric value. No `locale` calls or currency helpers needed.
- **No new files** — keep the change scoped to `app.py` and `database/db.py` is untouched.
- **Do not refactor** the existing `/register` or `/login` routes as part of this step. Scope is strictly the `/profile` route plus deletion of the now-unused `MOCK_*` constants.

## Definition of done

- [ ] `MOCK_USER`, `MOCK_STATS`, `MOCK_TRANSACTIONS`, and `MOCK_CATEGORIES` constants are removed from `app.py` along with the leading comment block that introduced them
- [ ] GET `/profile` while logged in returns HTTP 200 and renders the same page layout built in Step 4
- [ ] GET `/profile` without being logged in redirects to `/login` (existing auth guard still works)
- [ ] The user info card shows the logged-in user's real `name`, `email`, and a `Member since {Month YYYY}` value derived from `users.created_at`
- [ ] The avatar shows initials computed from the user's name (e.g. "DU" for "Demo User", "G" for "Ganesh")
- [ ] The Total Spent stat equals the sum of the logged-in user's expenses
- [ ] The Transactions stat equals the count of the logged-in user's expenses
- [ ] The Top Category stat is the category with the largest total spend, or empty if there are no expenses
- [ ] The recent transactions table shows the logged-in user's expenses, ordered by date descending, with columns Date / Description / Category badge / Amount
- [ ] The By Category section shows one row per category present in the user's expenses, sorted by total descending, each with a name, amount, and percent-of-total bar
- [ ] GET `/profile?date_from=2026-06-01&date_to=2026-06-30` filters both the stats and the table to expenses within that inclusive range
- [ ] GET `/profile` with no query params shows all of the user's expenses ("All Time")
- [ ] The "This Month" preset link is `?date_from=<first-of-this-month>&date_to=<today>` and filters correctly
- [ ] The "Last 3 Months" preset link is `?date_from=<first-of-3-months-ago>&date_to=<today>` and filters correctly
- [ ] The "Last 6 Months" preset link is `?date_from=<first-of-6-months-ago>&date_to=<today>` and filters correctly
- [ ] The active preset button is visually marked active when its date range matches the current filter (the template already does this; verify it still works)
- [ ] Malformed date query params (e.g. `?date_from=foo`) do not crash the route — they are silently ignored
- [ ] When the filtered result is empty: stats show `₹0.00` / `0` / `—`, the table shows the "No expenses found for this period." row, and the category list renders empty
- [ ] When the logged-in user has zero expenses in the DB, the page still renders cleanly (no exceptions)
- [ ] A second registered user does not see the first user's expenses or stats (row-level scoping works)
- [ ] Signing in as `demo@spendly.com` / `demo123` shows the same 8 seeded expenses that Step 4's mock page displayed (same categories, same approximate amounts — but as real data, not the `MOCK_TRANSACTIONS` list)
- [ ] All SQL uses parameterised statements (no f-strings, no `%`, no `+` concatenation in SQL)
- [ ] Every `get_db()` call in the route is closed in a `finally` block
- [ ] `database/db.py` is unchanged
- [ ] `templates/profile.html` is unchanged
- [ ] No new pip packages are added
- [ ] No new files are created
- [ ] App starts without errors and the navbar still greets the logged-in user with "Hello, {name}"
- [ ] Can verify end-to-end by running `python app.py`, signing in as `demo@spendly.com` / `demo123`, viewing `/profile`, and confirming the Total Spent, Transactions count, Top Category, recent transactions table, and By Category list all reflect the seeded data — then registering a second user, signing in as them, and confirming the page is empty (not the demo user's data).
