import os
from authors.settings.base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SENDING_MAIL = False

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
FROM_EMAIL = 'test@test.com'
DOMAIN = config('DOMAIN', default='')

