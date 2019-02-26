import os
from authors.settings.base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME', default = 'legion_backend'),
        'USER': config('DB_USER', default = 'legion'),
        'PASSWORD': config('DB_PASSWORD', default = '&L3g10n'),
        'HOST': config('DB_HOST'),
        'PORT': '',
    }
}
