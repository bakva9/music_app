web: gunicorn config.wsgi --bind 0.0.0.0:${PORT:-10000}
release: python manage.py migrate && python manage.py collectstatic --noinput && python manage.py seed_songs
