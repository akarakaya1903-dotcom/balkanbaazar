#!/usr/bin/env bash
# Sunucu disi (sifreli) yedegi kurar. Tekrar calistirmak guvenli.
#   Kullanim:  bash /var/www/balkanbaazar/deploy/setup-offsite-backup.sh
# Once rclone'da bir "uzak depo" tanimlanmis olmali (Google Drive, Backblaze B2, Dropbox, SFTP...).
set -euo pipefail
KEY=/root/.balkanbaazar-backup-key
CONF=/etc/balkanbaazar-offsite.conf

if ! command -v rclone >/dev/null 2>&1; then
  echo ">> rclone kuruluyor..."
  apt-get update -qq && apt-get install -y -qq rclone
fi

if [ ! -f "$KEY" ]; then
  umask 077
  openssl rand -base64 48 > "$KEY"
  chmod 600 "$KEY"
  echo
  echo "================ COK ONEMLI ================"
  echo "Yedekler bu anahtarla sifreleniyor. Anahtar kaybolursa yedekler ACILAMAZ."
  echo "Su satiri sifre yoneticine / guvenli bir yere KOPYALA (sunucu disinda):"
  echo
  cat "$KEY"
  echo
  echo "============================================"
  read -rp "Anahtari sunucu disinda sakladim (e yaz): " OKK
  [ "$OKK" = "e" ] || { echo "Iptal. Anahtari kaydedip tekrar calistir."; exit 1; }
fi

echo
echo "Tanimli rclone depolari:"; rclone listremotes || true
echo
if [ -z "$(rclone listremotes 2>/dev/null)" ]; then
  cat <<'HELP'
Henuz bir depo yok. Olusturmak icin:  rclone config
  - n (yeni) -> ad ver (orn. yedek) -> turu sec:
      * Backblaze B2 (10 GB ucretsiz, sunucuda kolay)   veya
      * Google Drive (sunucuda tarayici yok: kendi bilgisayarinda 'rclone authorize "drive"' calistirip kodu yapistir)
  - Bittikten sonra bu betigi tekrar calistir.
HELP
  exit 0
fi

read -rp "Kullanilacak depo adi (orn. yedek): " NAME
read -rp "Depo icindeki klasor (orn. balkanbaazar-yedek): " FOLDER
read -rp "Kac gun saklansin [30]: " DAYS; DAYS=${DAYS:-30}
REMOTE="${NAME%:}:${FOLDER}"
rclone mkdir "$REMOTE"
printf 'REMOTE=%q\nKEEP_DAYS=%s\n' "$REMOTE" "$DAYS" > "$CONF"
chmod 600 "$CONF"

[ -f /usr/local/bin/balkanbaazar-backup ] || install -m 755 /var/www/balkanbaazar/deploy/backup.sh /usr/local/bin/balkanbaazar-backup
install -m 755 /var/www/balkanbaazar/deploy/backup.sh /usr/local/bin/balkanbaazar-backup
echo ">> Ilk sunucu disi yedek aliniyor..."
/usr/local/bin/balkanbaazar-backup
echo
echo "Tamam. Kontrol:  rclone ls $REMOTE"
echo "Geri yukleme (veritabani):"
echo "  rclone copy $REMOTE/db-TARIH.sql.gz.enc /tmp/"
echo "  openssl enc -d -aes-256-cbc -pbkdf2 -pass file:$KEY -in /tmp/db-TARIH.sql.gz.enc -out /tmp/db.sql.gz"
echo "  gunzip -c /tmp/db.sql.gz | sudo -u postgres psql balkanbaazar"
