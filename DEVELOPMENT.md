# Development Guide — Media Planner

This guide shows how to run the project locally for development using Docker Compose and the local Python environment.

Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for running management commands locally)
- Node.js + pnpm (for frontend)

Quick start (Docker Compose)
1. Copy `.env.example` to `.env` and update credentials if needed.
2. Start services:

```powershell
# from repo root
docker compose up -d
```

This brings up:
- Postgres
- Redis
- MinIO (object storage)
- Backend (Django)
- Frontend (Vite)
- (Optional) Celery worker

Run migrations and seed data

```powershell
# run migrations
docker compose exec backend python manage.py migrate
# seed demo data
docker compose exec backend python manage.py seed_dev
```

Run Celery worker (dev)

```powershell
# start a worker attached (dev)
docker compose exec backend celery -A backend worker -l info
```

Run backend locally (without Docker)

```powershell
# assuming you have python environment activated
$env:DATABASE_URL = 'postgresql://postgres:password@localhost:5432/media_planner'
python backend/manage.py migrate
python backend/manage.py seed_dev
python backend/manage.py runserver
```

Run tests

```powershell
# in repo root
pushd backend; python manage.py test; popd
```

CI-friendly tests and RS256 notes
--------------------------------

We support two quick test modes for CI and local developers:

- Fast unit tests (default CI job): run with an in-memory SQLite DB using `config.test_settings`. This exercises most business logic (including license verification) without requiring Postgres.
- Integration tests (optional CI job): run against a Postgres service (via Docker action services) to run migrations and DB-dependent tests.

How to run fast tests locally (recommended for quick feedback):

```powershell
$env:DJANGO_SETTINGS_MODULE='config.test_settings'
python -m django test -v 2
```

RS256 tests
-----------

RS256 tests require Python cryptography support (the `cryptography` package) so PyJWT can use PEM keys. For developer convenience we include a dev RSA keypair under `backend/licenses/keys/` used only for local/dev testing. In CI we install `cryptography` so RS256 tests can run in the pipeline.

If your environment lacks `cryptography`, RS256 unit tests will be skipped to avoid false negatives. To enable RS256 tests locally, install the project requirements listed in `backend/requirements.txt` (or pip install `cryptography` directly).


Useful tips
- To run Celery in 'eager' mode for tests, set `CELERY_TASK_ALWAYS_EAGER=True` in your test settings.
- For local S3 emulation we use MinIO; access console at `http://localhost:9001` (default creds from `.env`).

Troubleshooting
- If you get DB connection errors, confirm Postgres is running and the `DATABASE_URL` matches the `.env` values.
- If worker tasks are not executing, ensure Redis is up and the worker has been started.

Offline license activation (developer flow)
----------------------------------------

1. Generate an activation request (prints JSON with `tenant_id` and `machine_hash`):

```powershell
# from repo root
pushd backend; python manage.py request_activation <tenant_id>; popd
```

2. The vendor will sign this payload and return a signed JWT token. For local testing you can create a HS256 token with the shared secret configured in `LICENSE_PUBLIC_KEY`.

3. Activate the license using the admin user (must belong to the tenant):

```powershell
# JSON body
curl -X POST 'http://localhost:8000/api/licenses/activate/' -H 'Content-Type: application/json' -d '{"token": "<signed-token>"}'
```

4. The middleware `licenses.middleware.LicenseEnforceMiddleware` will block requests (HTTP 402) for tenants without an active license. You can disable the middleware in development by removing it from `MIDDLEWARE` in `backend/config/settings.py`.

Dev RSA key handling (RS256 tests)
---------------------------------

For convenience a development RSA keypair is included at `backend/licenses/keys/dev_private.pem` and `backend/licenses/keys/dev_public.pem`. These are intended for local development and test runs only. Recommended practices:

- Keep the dev keypair for local dev to make it easy to sign/verify RS256 activation tokens.
- For CI, install `cryptography` so the RS256 tests can run against the committed dev public key, or (more secure) store production-like keys in CI secrets and reference them in the workflow.
- To regenerate a dev keypair locally:

```powershell
# generate 2048-bit RSA key (dev)
openssl genpkey -algorithm RSA -out backend/licenses/keys/dev_private.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -in backend/licenses/keys/dev_private.pem -pubout -out backend/licenses/keys/dev_public.pem
```

- To enable RS256 tests locally, ensure your Python env has `cryptography` installed (pip install cryptography) and run the tests with `DJANGO_SETTINGS_MODULE=config.test_settings`.

If you'd prefer not to commit private keys to the repository, move the keys into a secure location and add `backend/licenses/keys/` to `.gitignore`, and update `DEVELOPMENT.md` to instruct devs to generate their own keypair before running RS256 tests.


