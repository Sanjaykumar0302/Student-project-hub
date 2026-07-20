# StudentProjectHub

A web platform where students submit custom academic/college project requests, and an admin
builds and delivers them for a fee. Built with Flask, SQLAlchemy, and Bootstrap 5.

## What's included

- **Student side**: register/login, submit a project request (type, description, deadline,
  package tier, optional requirement file), track status through a 5-stage pipeline
  (Pending → Accepted → Working → Completed → Delivered), pay to unlock deliverables, download files.
- **Admin side**: dashboard with live stats, manage all project requests, move projects through
  status stages, upload completed deliverables, leave internal notes per project, view students,
  analytics with charts, manage package tiers (create/edit/hide).
- **Payments**: Razorpay order creation + signature verification, with a simulated checkout
  fallback so the whole flow is testable without live API keys.
- **Notifications**: in-app notifications for both roles (new requests, status changes, payment
  confirmations), with a polling unread-count badge in the navbar.
- **Auth**: registration, login, logout, forgot/reset password (console-logged reset link — see
  "What's stubbed" below).
- Basic **pytest** suite covering auth, project workflow, and public routes.

## What's stubbed (needs your own credentials to go fully live)

| Feature | Current behavior | To make it real |
|---|---|---|
| Razorpay payments | If no real API keys are set in `.env`, checkout uses a **simulated** "Pay" button that marks the project as paid without a real transaction. | Get test keys from the [Razorpay dashboard](https://dashboard.razorpay.com/app/keys) and set `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` in `.env`. |
| Password reset email | The reset link is printed to the server console/log instead of emailed. | Wire up Flask-Mail (or any provider) in `routes/auth.py::forgot_password` and send `reset_url` instead of printing it. |
| Contact form | Flashes a "thanks" message; the message isn't stored or emailed anywhere. | Save to DB or send via email in `routes/home.py::contact`. |

## Setup

```bash
# 1. Create a virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# edit .env - at minimum change SECRET_KEY and ADMIN_PASSWORD

# 4. Create the database, default packages, and an admin account
python seed.py

# 5. Run the app
python run.py
```

Visit `http://localhost:5000`. Log in as admin with the email/password you set in `.env`
(`ADMIN_EMAIL` / `ADMIN_PASSWORD`, defaults are `admin@studentprojecthub.com` / `ChangeMe123!`).

Register a normal account through the UI to try the student flow.

## Running tests

```bash
pip install pytest   # already in requirements.txt
pytest
```

Tests run against an in-memory SQLite database, so they won't touch your real `instance/` DB.

## Deploying to production

The app now auto-detects its environment: give it a Postgres `DATABASE_URL` and it uses
Postgres; give it `S3_BUCKET` credentials and it stores files in S3-compatible object storage.
Leave both unset and it falls back to local SQLite + local disk (fine for `python run.py`, **not**
fine for most hosting platforms, which wipe local disk on every deploy/restart).

This section deploys on a fully free stack: **Neon** (Postgres), **Cloudflare R2** (file storage),
**Render** (app hosting). Total cost: $0. The only real tradeoff is Render's free tier sleeps
after 15 minutes idle and takes 30-60s to wake up - upgrade the web service to Starter ($7/mo)
later if you want it always-on.

### 1. Database - Neon

1. Sign up at [neon.tech](https://neon.tech) (no card required) and create a project.
2. On the project dashboard, copy the **pooled** connection string (hostname contains
   `-pooler`) - this handles connection bursts much better than the direct one.
3. Save it somewhere; you'll paste it into Render as `DATABASE_URL` in step 3. It looks like
   `postgresql://user:password@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require`.

### 2. File storage - Cloudflare R2

1. Sign up at [dash.cloudflare.com](https://dash.cloudflare.com), go to **R2 Object Storage**,
   create a bucket (e.g. `studentprojecthub-files`).
2. **R2 → Manage API Tokens → Create API Token** with Object Read & Write permissions scoped to
   that bucket. Save the Access Key ID and Secret Access Key - the secret is shown once.
3. Note your **Account ID** (shown on the R2 overview page). Your endpoint URL is
   `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`.
4. **Required for avatars to keep working**: open the bucket → **Settings → Public Access** and
   enable the public development URL (or connect a custom domain). Copy that public URL - you'll
   set it as `S3_PUBLIC_BASE_URL`. Without this step, avatar photos will break after 7 days
   (the code falls back to a temporary signed URL if no public URL is configured).

### 3. App hosting - Render

1. Push this project to a GitHub repo.
2. On [render.com](https://render.com), **New → Web Service**, connect the repo.
   - Runtime: Python 3
   - Build command: `pip install -r requirements.txt && python seed.py`
     (running `seed.py` on every build is intentional and safe - it only creates the admin
     account and default packages the first time; every build after that it's a no-op. This is
     also how you seed the database at all, since Render's free tier has **no shell access**.)
   - Start command: `gunicorn run:app --workers 2 --timeout 120`
   - Instance type: Free
3. Add these environment variables in the Render dashboard:

   | Key | Value |
   |---|---|
   | `SECRET_KEY` | generate one, e.g. `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `FLASK_ENV` | `production` |
   | `DATABASE_URL` | the Neon pooled connection string from step 1 |
   | `S3_BUCKET` | your R2 bucket name |
   | `S3_ACCESS_KEY_ID` / `S3_SECRET_ACCESS_KEY` | from step 2 |
   | `S3_ENDPOINT_URL` | `https://<ACCOUNT_ID>.r2.cloudflarestorage.com` |
   | `S3_REGION` | `auto` |
   | `S3_PUBLIC_BASE_URL` | the public bucket URL from step 2 |
   | `ADMIN_EMAIL` / `ADMIN_PASSWORD` / `ADMIN_NAME` | your real admin login |
   | `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` | leave blank for simulated checkout, or your real test/live keys |

4. Deploy. Render builds, runs `seed.py` (creates your admin account + default packages), and
   starts the app. First load will be slow (cold start); after that it's normal speed until it
   sleeps again from inactivity.

A `render.yaml` is included in the project root if you'd rather use Render's Blueprint
(infra-as-code) flow instead of clicking through the dashboard - open it and fill in the
`sync: false` values after import.

### Alternative: Railway

Railway works the same way (Postgres via Neon, files via R2, same env vars) - the difference is
just its own dashboard for setting env vars and a `Procfile`-based start command, which is
already included in this project. Railway's free allowance is a small monthly credit rather than
always-free hours, so expect it to run out faster than Render's free tier on an idle project.

### If you'd rather not deal with any of this: a VPS

Everything above exists to work around platforms that wipe local disk. If you'd prefer to just
keep SQLite and local file storage exactly as they are with **zero code changes**, a cheap VPS
(DigitalOcean, Linode, Hetzner - roughly $4-6/mo) with a normal persistent disk works too: install
Python, clone the repo, run it behind `gunicorn` + `nginx` + a `systemd` service, skip all the S3
and Postgres setup entirely. Ask if you want those steps instead.

## Project structure

```
app.py              Flask application factory
config.py            Configuration (reads from .env)
extensions.py        Shared db / login_manager / migrate instances
forms.py             All WTForms form classes
run.py               Dev server entry point
seed.py              One-time DB setup: tables + default packages + admin account
Procfile             Production start command (Render/Railway)
render.yaml          Optional Render Blueprint (infra-as-code deploy)

models/              SQLAlchemy models (one file per entity)
routes/              Blueprints (one file per feature area)
services/            Business logic - file handling, notifications, project status, dashboard
                     stats, and storage_service.py (S3-compatible storage / local disk switch)
utils/                Decorators, constants, validators, helpers

templates/           Jinja2 templates, organized by area (home/auth/student/admin/errors)
static/              CSS, JS, images
uploads/             Uploaded requirement docs and completed deliverables (gitignored)
instance/            Local SQLite DB lives here at runtime (gitignored)
migrations/          Empty until you run `flask db init` (Flask-Migrate) if you want migrations
tests/               pytest suite
```

## Notes on the folder structure

If you're comparing this against an earlier draft of the folder layout: the original sketch had
both a top-level `models.py` **and** a `models/` package, which would have collided on import.
This build keeps `models/` as a package (one file per entity) and drops the flat `models.py`.
Similarly, the SQLite file lives in `instance/` (Flask's convention) rather than a separate
`database/` folder.

## Default package tiers (created by `seed.py`)

- **Basic** - ₹499 - completed project ZIP + basic setup instructions
- **Premium** - ₹999 - source code + report + presentation + DB dump + installation guide

Edit these anytime from **Admin → Settings** once you're logged in as admin.
