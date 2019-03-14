from authors.settings.base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME', default='legion_backend'),
        'USER': config('DB_USER', default='legion'),
        'PASSWORD': config('DB_PASSWORD', default='&L3g10n'),
        'HOST': config('DB_HOST'),
        'PORT': '',
    }
}

DOMAIN = config('DOMAIN', default='')
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
FROM_EMAIL = config('EMAIL_FROM', default='verify@authorsheaven.com')
