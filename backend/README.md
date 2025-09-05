# Backend (Django)

This folder will contain the Django backend for Media Planner.

Quick start (when the repo is scaffolded):

- Build and run services:

  docker-compose up --build

- Enter backend container or activate venv locally and run:

  python manage.py migrate
  python manage.py createsuperuser
  python manage.py runserver 0.0.0.0:8000

Notes:
- Settings should read configuration from environment variables (`DATABASE_URL`, `REDIS_URL`, `S3_*`).
- Use UUID primary keys for public models and add `created_at`/`updated_at` timestamps.
