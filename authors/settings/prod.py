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

EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
FROM_EMAIL = config('EMAIL_FROM', default='test@example.com')
