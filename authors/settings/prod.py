import os
import dj_database_url
from authors.settings.base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG')

ALLOWED_HOSTS = config('ALLOWED_HOSTS')

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, "static")

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}
