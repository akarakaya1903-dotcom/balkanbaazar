"""Site saglik kontrolu (cron her 5 dk). Sorun olursa STAFF_NOTIFY_EMAILS adreslerine e-posta atar.

Kontroller: genel adres yanit veriyor mu, veritabani, disk doluluk, gece yedegi taze mi, sunucu disi yedek taze mi.
Ayni sorun icin tek e-posta gonderir; duzelince 'duzeldi' e-postasi gonderir."""
import json
import shutil
import time
from pathlib import Path

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand

STATE = Path("/var/tmp/balkanbaazar-monitor.json")
BACKUP_DIR = Path("/var/backups/balkanbaazar")
OFFSITE_STAMP = BACKUP_DIR / ".offsite-ok"
THRESHOLD = {"site": 2}  # site 2 ardisik kontrolde (10 dk) yanit vermezse uyar; digerleri hemen


def _problems():
    found = {}
    try:
        import requests
        r = requests.get(settings.SITE_URL.rstrip("/") + "/saglik/", timeout=15)
        if r.status_code != 200 or r.text.strip() != "ok":
            found["site"] = f"{settings.SITE_URL}/saglik/ yaniti: HTTP {r.status_code}"
    except Exception as exc:
        found["site"] = f"Site yanit vermiyor ({exc.__class__.__name__})"
    try:
        from django.db import connection
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
    except Exception as exc:
        found["db"] = f"Veritabani hatasi ({exc.__class__.__name__})"
    try:
        du = shutil.disk_usage("/")
        pct = du.used * 100 // du.total
        if pct >= 85:
            found["disk"] = f"Disk %{pct} dolu"
    except Exception:
        pass
    if BACKUP_DIR.exists():
        dbs = sorted(BACKUP_DIR.glob("db-*.sql.gz"), key=lambda p: p.stat().st_mtime)
        if not dbs:
            found["backup"] = "Hic veritabani yedegi yok"
        elif time.time() - dbs[-1].stat().st_mtime > 36 * 3600:
            found["backup"] = f"Son yedek 36 saatten eski ({dbs[-1].name})"
        if Path("/etc/balkanbaazar-offsite.conf").exists():
            if not OFFSITE_STAMP.exists() or time.time() - OFFSITE_STAMP.stat().st_mtime > 36 * 3600:
                found["offsite"] = "Sunucu disi yedek 36 saattir basarisiz/eski"
    return found


class Command(BaseCommand):
    help = "Site saglik kontrolu; sorun olursa e-posta gonderir."

    def handle(self, *args, **opts):
        try:
            state = json.loads(STATE.read_text())
        except Exception:
            state = {}
        found = _problems()
        new_state, alerts, recovered = {}, [], []
        for key, text in found.items():
            prev = state.get(key, {})
            count = prev.get("count", 0) + 1
            alerted = prev.get("alerted", False)
            if not alerted and count >= THRESHOLD.get(key, 1):
                alerts.append(text)
                alerted = True
            new_state[key] = {"count": count, "alerted": alerted, "text": text}
        for key, prev in state.items():
            if key not in found and prev.get("alerted"):
                recovered.append(prev.get("text", key))
        try:
            STATE.write_text(json.dumps(new_state))
        except Exception:
            pass
        to = settings.STAFF_NOTIFY_EMAILS
        if (alerts or recovered) and to:
            lines = []
            if alerts:
                lines += ["SORUN:"] + [f" - {a}" for a in alerts]
            if recovered:
                lines += ["DUZELDI:"] + [f" - {r}" for r in recovered]
            subject = "[Balkan Baazar] " + ("SORUN" if alerts else "Duzeldi")
            try:
                send_mail(subject, "\n".join(lines) + f"\n\n{settings.SITE_URL}", settings.DEFAULT_FROM_EMAIL, to)
            except Exception as exc:
                self.stderr.write(f"E-posta gonderilemedi: {exc}")
        self.stdout.write("Sorun yok." if not found else "Sorunlar: " + "; ".join(found.values()))
