#!/usr/bin/env bash
set -e
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations market
python manage.py migrate
python manage.py seed --reset
echo ""
echo "Hazir. Calistir:  source venv/bin/activate && python manage.py runserver"
