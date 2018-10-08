#!/usr/bin/env sh

python3 manage.py migrate
python manage.py collectstatic --noinput
gunicorn --forwarded-allow-ips=* --bind 0.0.0.0:8080 -w 4 app.wsgi:application
