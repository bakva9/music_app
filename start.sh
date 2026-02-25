#!/usr/bin/env bash

gunicorn config.wsgi --bind 0.0.0.0:${PORT:-10000} --timeout 120
