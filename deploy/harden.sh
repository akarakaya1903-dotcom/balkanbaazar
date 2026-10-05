#!/usr/bin/env bash
# Sunucu sertlestirme: fail2ban (SSH kaba kuvvet korumasi), otomatik guvenlik guncellemeleri, /media/ icin nosniff.
# Tekrar calistirmak guvenli.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y fail2ban unattended-upgrades
systemctl enable --now fail2ban
SITE=/etc/nginx/sites-available/balkanbaazar
if grep -q "location /media/" "$SITE" && ! grep -q "nosniff" "$SITE"; then
  sed -i -E 's|^(\s*)location /media/ \{|\1location /media/ {\n\1    add_header X-Content-Type-Options nosniff;|' "$SITE"
fi
nginx -t && systemctl reload nginx
echo "fail2ban durumu:"; fail2ban-client status sshd || true
echo "Tamam."
