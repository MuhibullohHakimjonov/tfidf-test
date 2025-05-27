#!/bin/sh

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Start the app
echo "Starting server..."
gunicorn config.wsgi:application --bind 0.0.0.0:8000
