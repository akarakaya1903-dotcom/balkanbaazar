"""Basit bot korumasi: gizli tuzak alani + formun cok hizli gonderilmesini engelleme. Anahtar gerektirmez."""
import time

from django.core import signing

SALT = "bb-antispam"
MIN_SECONDS = 3
MAX_SECONDS = 6 * 3600


def make_token():
    return signing.dumps(int(time.time()), salt=SALT)


def looks_like_bot(request):
    """POST isteginde tuzak alani doluysa ya da form 3 saniyeden kisa surede gonderildiyse True."""
    if request.POST.get("website"):
        return True
    try:
        started = signing.loads(request.POST.get("bbts", ""), salt=SALT, max_age=MAX_SECONDS)
    except Exception:
        return True
    return (time.time() - started) < MIN_SECONDS
