release: python manage.py makemigrations --settings=authors.settings.prod
release: python manage.py migrate --settings=authors.settings.prod

web: gunicorn authors.wsgi
