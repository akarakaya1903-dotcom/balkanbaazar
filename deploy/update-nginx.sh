#!/usr/bin/env bash
# Buyuk yuklemeler, video oynatma (Range) ve zaman asimi ayarlari. Tekrar calistirmak guvenli.
set -euo pipefail
SITE=/etc/nginx/sites-available/balkanbaazar
cat > /etc/nginx/conf.d/balkanbaazar-upload.conf <<'UP_EOF'
client_body_timeout 600s;
send_timeout 600s;
UP_EOF
cat > /etc/nginx/conf.d/balkanbaazar-speed.conf <<'SP_EOF'
gzip_comp_level 5;
gzip_min_length 512;
gzip_vary on;
gzip_proxied any;
gzip_types text/css application/javascript application/json application/xml text/xml image/svg+xml text/plain application/manifest+json;
SP_EOF
sed -i -E 's/client_max_body_size [0-9]+M;/client_max_body_size 500M;/' "$SITE"
if ! grep -q "location /media/" "$SITE"; then
  sed -i -E 's|^(\s*)location / \{|\1location /media/ {\n\1    alias /var/www/balkanbaazar/media/;\n\1    expires 7d;\n\1}\n\n\1location / {|' "$SITE"
fi
if ! grep -q "proxy_read_timeout" "$SITE"; then
  sed -i -E 's|^(\s*)proxy_pass http://127.0.0.1:([0-9]+);|\1proxy_pass http://127.0.0.1:\2;\n\1proxy_read_timeout 300s;\n\1proxy_send_timeout 300s;|' "$SITE"
fi
sed -i 's/--workers 3$/--workers 3 --timeout 180/' /etc/systemd/system/balkanbaazar.service
cat > /etc/cron.d/balkanbaazar <<'CRON_EOF'
0 3 * * * root cd /var/www/balkanbaazar && set -a && . /etc/balkanbaazar.env && set +a && ./venv/bin/python manage.py expire_listings >> /var/log/balkanbaazar-expire.log 2>&1
*/10 * * * * root cd /var/www/balkanbaazar && set -a && . /etc/balkanbaazar.env && set +a && ./venv/bin/python manage.py compress_videos >> /var/log/balkanbaazar-video.log 2>&1
*/30 * * * * root cd /var/www/balkanbaazar && set -a && . /etc/balkanbaazar.env && set +a && ./venv/bin/python manage.py notify_saved_searches >> /var/log/balkanbaazar-saved.log 2>&1
*/5 * * * * root cd /var/www/balkanbaazar && set -a && . /etc/balkanbaazar.env && set +a && ./venv/bin/python manage.py check_site >> /var/log/balkanbaazar-monitor.log 2>&1
CRON_EOF
sed -i -E 's/expires 7d;/expires 30d;/' "$SITE"
systemctl daemon-reload
nginx -t
systemctl reload nginx
systemctl restart balkanbaazar
echo "Tamam."
