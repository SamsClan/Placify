# Placify

A full-stack placement management system connecting **students**, **companies**, and **placement admins** — built with a Flask + Celery + Redis backend and a Vue 3 SPA frontend.

Students discover and apply to placement drives, companies post openings and manage applicants, and admins moderate the whole ecosystem with real-time analytics.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3 (Composition API, `<script setup>`), Vue Router, Pinia, Axios, Bootstrap 5, Vite |
| Backend | Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-Caching, Flask-Mail, Flask-CORS |
| Async jobs | Celery (worker + beat) with Redis as broker & result backend |
| Charts | Matplotlib (server-rendered, embedded as base64 PNG) |
| Email (dev) | Mailpit — local SMTP catcher, no real emails ever leave your machine |
| Database | SQLite (dev) via SQLAlchemy — swappable for Postgres/MySQL via `DATABASE_URL` |

---

## Features

### Student
- Browse & filter placement drives, apply with resume link + cover letter (paginated results)
- Track application status (Applied → Shortlisted → Selected/Rejected)
- Profile management, notifications, **export application history as CSV** (async job) — available on both the dashboard and the Applications page

### Company
- Post placement drives with eligibility, salary, skills, deadlines
- Review & update applicant status, manage shortlisted/selected candidates, track joining details
- All list pages (jobs, applications, shortlisted, selected) are paginated

### Admin
- Approve/blacklist companies and students, approve/reject drives — all list pages paginated
- Clean dashboard with live stats, one-click triggers for background jobs, and a link out to a dedicated **Analytics** page
- Full moderation across companies, students, drives, and applications

### Background jobs (Celery)
1. **Daily deadline reminders** — emails students about drives closing soon. Runs daily at 09:00 UTC (`celery beat`), or trigger instantly from the Admin Dashboard.
2. **Monthly activity report** — HTML email to the admin with drive/application/selection stats and embedded matplotlib charts. Runs on the 1st of every month at 00:00 UTC, or trigger instantly from the Admin Dashboard.
3. **CSV export** (user-triggered, async) — student clicks "Export applications as CSV" → job is queued → frontend polls status → download link appears on completion.

All emails route through **Mailpit** in development — see [Email setup](#email-setup-mailpit) below.

### Analytics (`/admin/analytics`)
A dedicated page (separate from the dashboard, linked via a "View analytics" card) with 5 matplotlib charts: applications by status, drives by status, 6-month applications/selections trend, top recruiting companies, and applications by department. The same charts are embedded directly in the monthly report email.

### Caching
- Dashboard stats, analytics charts, and search results are cached in Redis (60–120s TTL).
- Writes (approvals, blacklists, status changes, new applications/drives) **eagerly invalidate** the relevant cache keys, so data doesn't wait for TTL expiry to refresh.
- `GET /api/v1/cache` — debug endpoint listing every cached key, its value, and remaining TTL.

### Pagination
Every list view (Admin's Companies/Students/Drives/Applications, Company's Jobs/Applications/Shortlisted/Selected, Student's Jobs/Applications) uses a shared `PaginationControls` component + `usePagination` composable — 6 items per page, with compact page-number controls matching the app's navy/blue theme.

---

## Project Structure

```
Placement_Application_Portal 2/
├── backend/app.py             # WSGI entrypoint (flask run / gunicorn)
├── backend/celery_entrypoint.py  # Celery worker/beat entrypoint
├── backend/
│   ├── api/v1/
│   │   ├── auth_routes.py     # Login/register
│   │   ├── common.py          # Shared helpers: auth checks, serializers, caching, avatars, search
│   │   ├── admin_routes.py    # Admin dashboard, analytics, moderation, background-job triggers
│   │   ├── company_routes.py  # Company dashboard, jobs, applications, placements
│   │   └── student_routes.py  # Student dashboard, jobs, applications, exports, notifications
│   ├── controllers/
│   │   └── spa_controller.py  # Serves the built Vue SPA for all non-API routes
│   ├── models/                # SQLAlchemy models
│   ├── tasks/                 # Celery tasks: reminders.py, reports.py, exports.py
│   ├── utils/charts.py        # Matplotlib chart generation
│   ├── templates/emails/      # HTML/text email templates
│   ├── celery_app.py          # Celery config + beat schedule
│   ├── factory.py             # Flask app factory
│   └── run.py                 # Dev server entrypoint (seeds DB on first run)
└── frontend/
    ├── src/
    │   ├── views/              # Page components (Admin/Company/Student/Auth)
    │   ├── components/         # Shared UI: EntityCard, DetailHero, ChartCard, PaginationControls, StatusBadge, ...
    │   ├── composables/        # useDashboard, useTaskPolling, useApplicationExport, usePagination, useToast, ...
    │   ├── stores/              # Pinia stores
    │   └── styles/              # Design tokens (navy/blue theme)
    └── css/pages/public/        # Login/Register/Home page styles
```

**Why the API is split into 4 files:** `resource_routes.py` used to be a single ~1750-line file. It's now `common.py` (shared helpers + auth/search/avatar routes) plus one file per role (`admin_routes.py`, `company_routes.py`, `student_routes.py`), each registered as its own Blueprint in `api/v1/__init__.py`. Same 62 routes, same behavior — just organized by who calls them.

---

## Setup & Run

> **Shortcut:** once you've done the one-time installs below (Redis, Mailpit, the Python venv, `npm install`), you can bring up Redis + Mailpit + backend + Celery worker + Celery beat together with `./start_dev.sh` (stop them with `./stop_dev.sh`). Logs go to `logs/*.log`. The frontend (`npm run dev`) still runs in its own terminal separately. See [Convenience scripts](#convenience-scripts) below for details.

You'll need **5 terminals**: Redis, Mailpit, Backend, Celery worker, Frontend (+ an optional 6th for Celery beat).

### 0. Prerequisites
- Python 3.11+, Node.js 18+, Redis, Mailpit

### 1. Redis
```bash
# macOS: brew install redis (if not already installed)
redis-server
```

### 2. Mailpit (local email catcher)
```bash
# macOS: brew install mailpit
mailpit
```
This starts an SMTP server on `localhost:1025` and a web inbox at **http://localhost:8025**. Every email the app sends (reminders, monthly report) lands there — nothing is ever delivered to a real inbox, so it's safe to use with the seeded demo `@example.com` addresses.

### 3. Backend
```bash
cd "Placement_Application_Portal 2"
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt

# First run seeds the DB with an admin account + sample data
PORT=5001 python backend/run.py
```
Backend runs at `http://127.0.0.1:5001` (frontend's `.env` expects port `5001`).

**Default admin login:** `admin@placementportal.com` / `admin123`

### 4. Celery worker (new terminal)
```bash
cd "Placement_Application_Portal 2"
source .venv/bin/activate
celery -A backend.celery_entrypoint worker --loglevel=info
```

### 5. Celery beat (new terminal — optional, only needed to test the *scheduled* triggers)
```bash
cd "Placement_Application_Portal 2"
source .venv/bin/activate
celery -A backend.celery_entrypoint beat --loglevel=info
```

### 6. Frontend (new terminal)
```bash
cd "Placement_Application_Portal 2"/frontend
npm install
npm run dev
```
Open the printed URL (typically `http://localhost:5173`).

### Convenience scripts

After you've done the one-time setup above (Redis/Mailpit installed, `.venv` created with deps installed), `start_dev.sh` and `stop_dev.sh` save you from juggling 5 terminals every session.

```bash
./start_dev.sh
```
This will, for each service:
- Skip it if something's already listening on its port (so it never fights with a terminal you already have open).
- Otherwise launch it in the background, writing its output to `logs/<service>.log` and its PID to `.dev-pids/<service>.pid`.

It starts, in order: Redis, Mailpit, the Flask backend (port 5001), the Celery worker, and Celery beat. The frontend is **not** started by this script — run `npm run dev` in `frontend/` yourself, since you'll usually want that in its own terminal with visible hot-reload output.

Tail any log while things are running:
```bash
tail -f logs/worker.log      # watch reminder/report jobs get picked up
tail -f logs/backend.log
```

Sanity-check the broker is actually reachable before testing the Admin Dashboard buttons:
```bash
redis-cli ping   # should print PONG
```

Stop everything the script started:
```bash
./stop_dev.sh
```
(Anything that was already running before `start_dev.sh` — and so was left alone — is also left alone by `stop_dev.sh`.)

### Production-style single-server run (optional)
```bash
cd frontend && npm run build && cd ..
PORT=5001 python backend/run.py
```
Flask now serves the built SPA directly from `frontend/dist` at `http://127.0.0.1:5001` — no separate Vite server needed. Deep links (e.g. `/admin/dashboard` typed directly in the browser) work correctly thanks to the SPA catch-all route.

---

## Database Migrations

The project uses **Flask-Migrate** (Alembic) to manage schema changes. `migrations/` is already scaffolded with an initial migration that matches the schema your existing `backend/instance/placement_portal.db` was built with.

**You already have a database with real data — adopt migrations without touching it:**
```bash
export FLASK_APP=app.py
flask db stamp head
```
This just marks your existing database as "up to date" with the initial migration. It runs no SQL against your tables and doesn't touch your rows — your students/companies/drives are untouched.

**Setting up a brand new, empty database** (e.g. a fresh clone or CI):
```bash
export FLASK_APP=app.py
flask db upgrade
```
This creates every table from scratch via the migration instead of `db.create_all()`.

**Making a schema change going forward** (e.g. adding a column to a model):
```bash
export FLASK_APP=app.py
flask db migrate -m "describe the change"   # generates a new file in migrations/versions/
flask db upgrade                             # applies it
```
Always read the autogenerated migration before running `upgrade` — Alembic is good but not perfect, especially with SQLite (e.g. column renames show up as drop+add).

---

## Email setup (Mailpit)

The app sends two kinds of emails, both email-only (no SMS/chat integrations):
1. Daily deadline reminders to students
2. Monthly activity report to the admin

`.env` is pre-configured to point at Mailpit:
```bash
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=false
MAIL_USE_SSL=false
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=placify@demo.com
```
Run `mailpit`, trigger a reminder/report from the Admin Dashboard, and refresh **http://localhost:8025** — the email (with rendered HTML and, for the monthly report, embedded charts) appears immediately.

If `MAIL_SERVER` is left blank, both jobs still run end-to-end (queued → processed → in-app notification created) but skip the send step — useful for testing the pipeline without any SMTP server running at all.

To use a real inbox instead of Mailpit, swap in real SMTP credentials (e.g. Gmail with an App Password) — but note the seeded student/company emails are all fake `@example.com` addresses, so you'd only see delivery for accounts you've pointed at a real address.

---

## Environment Variables

Create/edit `.env` in the project root:

```bash
SECRET_KEY=change-me-to-something-long-and-random   # min 32 bytes recommended
DATABASE_URL=sqlite:///instance/placement_portal.db

# Mailpit (see "Email setup" above) — swap for real SMTP creds if needed
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=false
MAIL_USE_SSL=false
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=placify@demo.com

REDIS_URL=redis://localhost:6379/0   # defaults to this if unset

# Optional tuning for the daily reminder job
REMINDER_DAYS_AHEAD=3          # notify students this many days before a drive's deadline
REMINDER_SCHEDULE_HOUR=9       # UTC hour the daily beat schedule fires
REMINDER_SCHEDULE_MINUTE=0
```
`frontend/.env` — `VITE_API_BASE_URL=http://127.0.0.1:5001` (already set).

---

## Viva Demonstration Guide

**Setup:** Have all terminals open (Redis, Mailpit, Backend, Worker, Beat, Frontend) so the examiner can see live logs. Keep `http://localhost:8025` (Mailpit inbox) open in a browser tab.

### a. Daily reminders (scheduled + email)
1. Admin Dashboard → **"Send deadline reminders now"**
2. Show the Celery worker terminal — task received & completed in real time
3. Toast confirms how many students were notified
4. Switch to the Mailpit tab and refresh — the reminder emails are all there
5. Point to `backend/celery_app.py`'s `beat_schedule` (`crontab(hour=9)`) — the button is a manual trigger of the same task the daily schedule runs automatically

### b. Monthly report (scheduled + HTML email with charts)
1. Admin Dashboard → **"Generate monthly report now"**
2. Worker log + toast confirm completion
3. Open the report in Mailpit — show the embedded matplotlib charts and stats rendered directly in the email body
4. Point to `crontab(day_of_month=1)` in `celery_app.py` for the automatic monthly run

### c. CSV export (user-triggered async job)
1. Student Dashboard (or Applications page) → **"Export applications as CSV"**
2. Show status flipping Pending → Processing → Completed (Network tab: polling `/api/v1/student/export-status/<task_id>`)
3. Download and open the CSV — Student ID, Company, Drive, Status, Dates
4. Worker log shows the task was processed asynchronously, not blocking the request

### d. Caching & performance
1. Open `GET /api/v1/cache` — shows every cached key, its value, and remaining TTL
2. Load the Admin Dashboard twice — second load is faster (cache hit)
3. Perform a write (e.g. approve a company) and reload the dashboard immediately — data updates instantly (eager invalidation), rather than waiting for the TTL
4. Explain the two-layer strategy: **eager invalidation** on writes for correctness + **TTL expiry** (60–120s) as a safety net for anything invalidation doesn't cover

### e. Analytics page
1. Admin Dashboard → **"View analytics"** card → `/admin/analytics`
2. Point out the 5 matplotlib charts, and that the same chart functions (`backend/utils/charts.py`) generate the images embedded in the monthly report email

### f. Modularized backend routes
Open `backend/api/v1/` and show `common.py` + `admin_routes.py` + `company_routes.py` + `student_routes.py` — each Blueprint owns only its role's endpoints, all sharing the same auth/caching/serializer helpers from `common.py`.

---

## Design Notes / Assumptions

- The frontend is a pure SPA — it talks exclusively to `/api/v1/*` (JWT-authenticated JSON API). The old session-based server-rendered routes have been removed and replaced with a single SPA catch-all (`backend/controllers/spa_controller.py`).
- Cache invalidation is pattern-based against Redis directly (`dashboard:admin:*`, `dashboard:company:{id}`, etc.) rather than per-key tracking, since Flask-Caching doesn't support wildcard deletion natively.
- Reminders and reports are email-only — no SMS or chat-webhook integrations.
- Without SMTP reachable (e.g. Mailpit not running), email-sending steps in reminders/report tasks fail gracefully per-recipient rather than crashing the whole job; the in-app notification is still created either way.
- Pagination is client-side (6 items/page) since list sizes are small enough for a placement portal; the backend returns full lists and the frontend slices them.
- `SECRET_KEY` in `.env` is a placeholder — replace with a long random value before any real deployment.
