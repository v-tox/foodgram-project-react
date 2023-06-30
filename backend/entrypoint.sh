#!/bin/sh

python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic --noinput --clear
gunicorn foodgram.wsgi:application --bind 0.0.0.0:"${BACKEND_PORT}" --reload