#!/usr/bin/env bash
# /admin/ adresine nginx'te ikinci bir sifre (HTTP basic auth) koyar. Tekrar calistirmak guvenli.
set -euo pipefail
SITE=/etc/nginx/sites-available/balkanbaazar
HT=/etc/nginx/.htpasswd-admin
read -rp "Admin icin ek kullanici adi: " U
read -rsp "Ek sifre: " P; echo
printf "%s:%s\n" "$U" "$(openssl passwd -apr1 "$P")" > "$HT"
chown root:www-data "$HT"; chmod 640 "$HT"
if ! grep -q "location /admin/" "$SITE"; then
  PORT=$(grep -oE 'proxy_pass http://127.0.0.1:[0-9]+' "$SITE" | head -1 | grep -oE '[0-9]+$')
  sed -i -E "s|^(\s*)location / \{|\1location /admin/ {\n\1    auth_basic \"Yonetim\";\n\1    auth_basic_user_file $HT;\n\1    proxy_pass http://127.0.0.1:$PORT;\n\1    proxy_set_header Host \$host;\n\1    proxy_set_header X-Real-IP \$remote_addr;\n\1    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;\n\1    proxy_set_header X-Forwarded-Proto \$scheme;\n\1}\n\n\1location / {|" "$SITE"
fi
nginx -t && systemctl reload nginx
echo "Tamam. /admin/ artik once bu ek sifreyi, sonra Django girisini isteyecek."
