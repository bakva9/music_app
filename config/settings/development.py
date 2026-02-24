from .base import *
import dj_database_url

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': dj_database_url.config(
        default='postgres://musicapp:musicapp123@localhost:5434/musicapp_dev'
    )
}

# Use simple static storage in development
STORAGES = {
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}
