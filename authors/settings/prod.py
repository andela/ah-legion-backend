import os
import dj_database_url
from authors.settings.base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}
