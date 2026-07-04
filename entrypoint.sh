#!/bin/sh
set -e

# Run migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Execute the command passed to docker-compose (gunicorn)
exec "$@"
