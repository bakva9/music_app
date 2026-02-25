#!/usr/bin/env bash

python manage.py migrate --noinput
gunicorn config.wsgi --bind 0.0.0.0:${PORT:-10000}
