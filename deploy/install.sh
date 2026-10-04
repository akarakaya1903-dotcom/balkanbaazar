#!/usr/bin/env bash
# Balkan Baazar - Ubuntu 24.04 VPS kurulum dosyasi.
# Kullanim (sunucuda, proje /var/www/balkanbaazar icine indirildikten sonra):
#   bash /var/www/balkanbaazar/deploy/install.sh
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "root olarak calistirin"; exit 1; }

DOMAIN="balkanbaazar.com"
APP_DIR="/var/www/balkanbaazar"
ENV_FILE="/etc/balkanbaazar.env"
[ -f "$APP_DIR/manage.py" ] || { echo "Proje $APP_DIR icinde bulunamadi. Once git clone yapin."; exit 1; }

read -rp  "Yonetici kullanici adi: " SU_USER
read -rp  "Yonetici e-posta (SSL icin de kullanilir): " SU_EMAIL
read -rsp "Yonetici sifresi: " SU_PASS; echo

echo ">> Programlar kuruluyor..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y python3-venv python3-pip nginx postgresql git certbot python3-certbot-nginx ufw openssl
ufw allow OpenSSH >/dev/null
ufw allow "Nginx Full" >/dev/null
ufw --force enable >/dev/null

if [ ! -f "$ENV_FILE" ]; then
  echo ">> Veritabani ve ayar dosyasi olusturuluyor..."
  DB_PASS="$(openssl rand -hex 16)"
  SECRET="$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')"
  sudo -u postgres psql -c "CREATE USER balkan WITH PASSWORD '${DB_PASS}';"
  sudo -u postgres psql -c "CREATE DATABASE balkanbaazar OWNER balkan;"
  cat > "$ENV_FILE" <<ENV_EOF
DJANGO_SECRET_KEY=${SECRET}
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=${DOMAIN},www.${DOMAIN}
DJANGO_CSRF_TRUSTED_ORIGINS=https://${DOMAIN},https://www.${DOMAIN}
DATABASE_URL=postgres://balkan:${DB_PASS}@localhost:5432/balkanbaazar
SITE_URL=https://${DOMAIN}
MEDIA_ROOT=${APP_DIR}/media
ENV_EOF
  chmod 600 "$ENV_FILE"
else
  echo ">> Ayar dosyasi zaten var, korunuyor."
fi

echo ">> Python paketleri kuruluyor..."
cd "$APP_DIR"
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo ">> Veritabani hazirlaniyor..."
set -a; . "$ENV_FILE"; set +a
./venv/bin/python manage.py migrate --no-input
./venv/bin/python manage.py collectstatic --no-input
./venv/bin/python manage.py shell -c "from market.models import Country; from django.core.management import call_command; Country.objects.exists() or call_command('seed')"
./venv/bin/python manage.py add_categories
DJANGO_SUPERUSER_USERNAME="$SU_USER" DJANGO_SUPERUSER_EMAIL="$SU_EMAIL" DJANGO_SUPERUSER_PASSWORD="$SU_PASS" \
  ./venv/bin/python manage.py createsuperuser --noinput || echo "(yonetici hesabi zaten var olabilir)"
mkdir -p "$APP_DIR/media"
chown -R www-data:www-data "$APP_DIR"

echo ">> Site servisi kuruluyor..."
cat > /etc/systemd/system/balkanbaazar.service <<'SERVICE_EOF'
[Unit]
Description=Balkan Baazar
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/balkanbaazar
EnvironmentFile=/etc/balkanbaazar.env
ExecStart=/var/www/balkanbaazar/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE_EOF
systemctl daemon-reload
systemctl enable balkanbaazar
systemctl restart balkanbaazar

echo ">> Nginx ayarlaniyor..."
cat > /etc/nginx/sites-available/balkanbaazar <<'NGINX_EOF'
server {
    listen 80;
    server_name __DOMAIN__ www.__DOMAIN__;
    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX_EOF
sed -i "s/__DOMAIN__/${DOMAIN}/g" /etc/nginx/sites-available/balkanbaazar
ln -sf /etc/nginx/sites-available/balkanbaazar /etc/nginx/sites-enabled/balkanbaazar
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

echo ">> SSL sertifikasi aliniyor..."
if certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos -m "$SU_EMAIL" --redirect; then
  echo "SSL tamam."
else
  echo "SSL kurulamadi (DNS henuz yonlenmemis olabilir). DNS hazir olunca su komutu calistir:"
  echo "certbot --nginx -d $DOMAIN -d www.$DOMAIN --agree-tos -m $SU_EMAIL --redirect"
fi

echo
echo "KURULUM BITTI. Siteyi ac: https://${DOMAIN}   Yonetim: https://${DOMAIN}/admin/"
