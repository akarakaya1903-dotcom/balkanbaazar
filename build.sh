#!/usr/bin/env bash
# Render build komutu: ./build.sh
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input

# Ilk kurulumda bir kez ornek ulkeler/kategoriler/magazalar yuklenir (veri varsa atlanir).
python manage.py shell -c "from market.models import Country; from django.core.management import call_command; Country.objects.exists() or call_command('seed')"
# Ek kategoriler (turizm, arac kiralama). Tekrar calistirmak guvenli.
python manage.py add_categories

# Yonetici hesabi: DJANGO_SUPERUSER_USERNAME / _EMAIL / _PASSWORD tanimliysa olusturur, varsa atlar.
python manage.py createsuperuser --no-input || true
