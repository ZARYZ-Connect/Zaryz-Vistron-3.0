#!/bin/sh
set -e

echo "==> Waiting for database at $DB_HOST:$DB_PORT..."

# Use a single-line python check — more reliable across shell environments
until python -c "import psycopg2, sys; psycopg2.connect(dbname='$DB_NAME', user='$DB_USER', password='$DB_PASSWORD', host='$DB_HOST', port='$DB_PORT'); sys.exit(0)" 2>/dev/null; do
  echo "   DB not ready, retrying in 2s..."
  sleep 2
done

echo "==> Database is ready."

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Starting Gunicorn..."
exec gunicorn vms_project.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
