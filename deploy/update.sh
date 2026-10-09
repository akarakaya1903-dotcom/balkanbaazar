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
# Tekrar calistirilmasi guvenli yardimci komutlar (yeni sayfa/kategori/ceviri/puan duzeltmeleri)
./venv/bin/python manage.py add_categories >/dev/null
./venv/bin/python manage.py add_pages >/dev/null
./venv/bin/python manage.py add_guides >/dev/null
./venv/bin/python manage.py make_thumbs >/dev/null
./venv/bin/python manage.py shrink_media >/dev/null
./venv/bin/python manage.py fix_ratings >/dev/null
# Yedek betigi /usr/local/bin'e kopyalandigi icin her guncellemede yenilenir
[ -f /usr/local/bin/balkanbaazar-backup ] && install -m 755 deploy/backup.sh /usr/local/bin/balkanbaazar-backup
chown -R www-data:www-data /var/www/balkanbaazar
systemctl restart balkanbaazar
# nginx ayarlari, zamanli gorevler (yedek, kayitli arama, video) - tekrar calistirmak guvenli
bash deploy/update-nginx.sh
echo "Guncelleme tamam."
