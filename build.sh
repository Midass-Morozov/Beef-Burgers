#!/usr/bin/env bash
# Выходим, если произошла ошибка
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate