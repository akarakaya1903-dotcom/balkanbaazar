#!/usr/bin/env bash
# Buyuk yuklemeler, video oynatma (Range) ve zaman asimi ayarlari. Tekrar calistirmak guvenli.
set -euo pipefail
SITE=/etc/nginx/sites-available/balkanbaazar
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
CRON_EOF
systemctl daemon-reload
nginx -t
systemctl reload nginx
systemctl restart balkanbaazar
echo "Tamam."
