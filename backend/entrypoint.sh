#!/bin/sh
set -e

# Wait for Postgres
until nc -z -v -w30 ${POSTGRES_HOST:-postgres} ${POSTGRES_PORT:-5432}; do
  echo "Waiting for postgres..."
  sleep 1
done

# Run migrations and start server if not explicit command
python manage.py migrate --noinput

# Create superuser if env vars provided (non-interactive)
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  echo "from django.contrib.auth import get_user_model; User = get_user_model();
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME','$DJANGO_SUPERUSER_EMAIL','$DJANGO_SUPERUSER_PASSWORD')" | python manage.py shell || true
fi

exec "$@"
