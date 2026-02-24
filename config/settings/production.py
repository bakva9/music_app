import os
from .base import *
import dj_database_url

DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
}
