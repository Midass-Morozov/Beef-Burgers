#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Создаем админа из переменных окружения (без вопросов)
python manage.py createsuperuser --noinput || true

python manage.py seed_data