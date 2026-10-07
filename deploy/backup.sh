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

# --- Sunucu disi yedek (istege bagli): /etc/balkanbaazar-offsite.conf varsa calisir ---
# Dosyalar yuklenmeden once AES-256 ile sifrelenir; anahtar yalniz bu sunucuda ve sende durur.
CONF=/etc/balkanbaazar-offsite.conf
KEY=/root/.balkanbaazar-backup-key
if [ -f "$CONF" ] && [ -f "$KEY" ] && command -v rclone >/dev/null 2>&1; then
  # shellcheck disable=SC1090
  . "$CONF"   # REMOTE=uzak_ad:klasor   KEEP_DAYS=30
  TMP="$DIR/.offsite-tmp"; rm -rf "$TMP"; mkdir -p "$TMP"; chmod 700 "$TMP"
  FILES=("$DIR/db-$STAMP.sql.gz")
  if [ "$(date +%u)" = "7" ]; then
    FILES+=("$DIR/media-$STAMP.tar.gz")
    [ -f "$DIR/private-$STAMP.tar.gz" ] && FILES+=("$DIR/private-$STAMP.tar.gz")
  fi
  OK=1
  for f in "${FILES[@]}"; do
    [ -f "$f" ] || continue
    openssl enc -aes-256-cbc -pbkdf2 -salt -pass "file:$KEY" -in "$f" -out "$TMP/$(basename "$f").enc" || OK=0
  done
  if [ "$OK" = "1" ] && rclone copy "$TMP" "$REMOTE" --quiet; then
    rclone delete "$REMOTE" --min-age "${KEEP_DAYS:-30}d" --quiet || true
    touch "$DIR/.offsite-ok"
    echo "Sunucu disi yedek yuklendi: $REMOTE"
  else
    echo "UYARI: sunucu disi yedek BASARISIZ ($REMOTE)" >&2
  fi
  rm -rf "$TMP"
fi
