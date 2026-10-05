#!/usr/bin/env bash
# Siteyi tek komutla gunceller:  bash /var/www/balkanbaazar/deploy/update.sh
set -euo pipefail
cd /var/www/balkanbaazar
git config --global --add safe.directory /var/www/balkanbaazar >/dev/null 2>&1 || true
echo ">> Kod cekiliyor..."
git pull
set -a; . /etc/balkanbaazar.env; set +a
echo ">> Paketler, veritabani, statik dosyalar..."
./venv/bin/pip install -q -r requirements.txt
./venv/bin/python manage.py migrate --no-input
./venv/bin/python manage.py collectstatic --no-input >/dev/null
chown -R www-data:www-data /var/www/balkanbaazar
systemctl restart balkanbaazar
echo "Guncelleme tamam."
