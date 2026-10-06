#!/usr/bin/env bash
# Yedegi kurar: /usr/local/bin/balkanbaazar-backup + her gece 02:30 cron + ilk yedek. Tekrar calistirmak guvenli.
set -euo pipefail
install -m 755 /var/www/balkanbaazar/deploy/backup.sh /usr/local/bin/balkanbaazar-backup
cat > /etc/cron.d/balkanbaazar-backup <<'CRON_EOF'
30 2 * * * root /usr/local/bin/balkanbaazar-backup >> /var/log/balkanbaazar-backup.log 2>&1
CRON_EOF
/usr/local/bin/balkanbaazar-backup
echo "Yedekleme kuruldu. Dosyalar: /var/backups/balkanbaazar"
