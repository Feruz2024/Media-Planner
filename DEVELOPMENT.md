
# Development Guide — Media Planner

## Recent Backend Progress (2025-09-12)

- All DRF permissions have been audited and enforced for tenants, stations, shows, dayparts, ratecards, licenses, and planner entities.
- Backend RBAC and JWT tests are implemented and passing for all endpoints.
- OpenAPI documentation (`backend/openapi.yaml`) is generated and up-to-date, covering all endpoints, request/response formats, and required permissions.
- To view or share API docs, use Swagger UI or Redoc with the OpenAPI file.


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

We support two quick test modes for CI and local developers:
- Fast unit tests (default CI job): run with an in-memory SQLite DB using `config.test_settings`. This exercises most business logic (including license verification) without requiring Postgres.
- Integration tests (optional CI job): run against a Postgres service (via Docker action services) to run migrations and DB-dependent tests.

$env:DJANGO_SETTINGS_MODULE='config.test_settings'
python -m django test -v 2
```

RS256 tests
-----------


If your environment lacks `cryptography`, RS256 unit tests will be skipped to avoid false negatives. To enable RS256 tests locally, install the project requirements listed in `backend/requirements.txt` (or pip install `cryptography` directly).

We recommend NOT committing private or production keys to the repository. Instead:

- Store the public key (PEM) in CI as a secret and expose it to the test job as the environment variable `LICENSE_PUBLIC_KEY` (the full PEM string) or provide a file path via `LICENSE_PUBLIC_KEY_PATH`.
- For local developer convenience you can generate a short-lived dev keypair, but treat the private key as sensitive and keep it outside the repo.

How to generate a local dev keypair (optional):

```powershell
# generate 2048-bit RSA key (dev)
openssl genpkey -algorithm RSA -out ~/.local-keys/dev_private.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -in ~/.local-keys/dev_private.pem -pubout -out ~/.local-keys/dev_public.pem
```

Set the public key for local testing by exporting the PEM (or pointing to the path):

```powershell


```

Test configuration and CI

- `backend/config/test_settings.py` will still use HS256 by default for fast unit tests. When CI runs RS256 tests, set `LICENSE_TOKEN_ALGORITHM=RS256` and provide `LICENSE_PUBLIC_KEY` in the workflow's environment.
- If you set `LICENSE_PUBLIC_KEY_PATH`, the application will read the file contents automatically. This permits mounting the key file from a secrets store in CI.

This approach keeps private keys out of source control and lets CI/ops manage production-like keys securely.
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

Dev RSA key handling (RS256 tests)
---------------------------------

Recommended practices:
- Do NOT commit private or production keys to the repository.
- For CI, store the public key (PEM) in repository secrets and reference it in the workflow as `LICENSE_PUBLIC_KEY`.
- For local development, generate your own dev keypair and keep the private key outside the repo. Example:

```powershell
# generate 2048-bit RSA key (dev)
openssl genpkey -algorithm RSA -out ~/.local-keys/dev_private.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -in ~/.local-keys/dev_private.pem -pubout -out ~/.local-keys/dev_public.pem
```

- To enable RS256 tests locally, ensure your Python env has `cryptography` installed (`pip install cryptography`) and run the tests with `DJANGO_SETTINGS_MODULE=config.test_settings`.
- Add `backend/licenses/keys/` to `.gitignore` to prevent accidental commits of key files.

Dependency management
---------------------
- All Python dependencies should be listed in `backend/requirements.txt`.
- Remove any unused or duplicate requirements files from the repo root.
