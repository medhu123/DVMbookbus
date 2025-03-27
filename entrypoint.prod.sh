#!/bin/sh


python manage.py collectstatic --noinput
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python -m gunicorn --bind 0.0.0.0:8000 --workers 3 mysite.wsgi:application