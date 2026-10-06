#!/usr/bin/env bash
# Gunluk yedek: veritabani (sikistirilmis) + her pazar medya arsivi. 14 gun / 4 hafta saklar.
set -euo pipefail
DIR=/var/backups/balkanbaazar
mkdir -p "$DIR"; chmod 700 "$DIR"
STAMP=$(date +%F)
sudo -u postgres pg_dump balkanbaazar | gzip > "$DIR/db-$STAMP.sql.gz"
if [ "$(date +%u)" = "7" ]; then
  tar -czf "$DIR/media-$STAMP.tar.gz" -C /var/www/balkanbaazar media
  [ -d /var/www/balkanbaazar/private ] && tar -czf "$DIR/private-$STAMP.tar.gz" -C /var/www/balkanbaazar private || true
fi
find "$DIR" -name 'db-*.sql.gz' -mtime +14 -delete
find "$DIR" -name 'media-*.tar.gz' -mtime +28 -delete
find "$DIR" -name 'private-*.tar.gz' -mtime +28 -delete
echo "Yedek alindi: $DIR ($(ls "$DIR" | wc -l) dosya)"
