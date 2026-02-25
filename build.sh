#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate

# Seed data (non-fatal — don't block deploy if seeding fails)
python manage.py seed_music_theory || echo "Warning: seed_music_theory failed, continuing..."
python manage.py seed_progressions || echo "Warning: seed_progressions failed, continuing..."
python manage.py seed_achievements || echo "Warning: seed_achievements failed, continuing..."
