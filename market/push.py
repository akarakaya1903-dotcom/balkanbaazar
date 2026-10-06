"""Web Push (telefon/tarayici anlik bildirimi). pywebpush ve VAPID anahtarlari gerekir."""
import json
import threading

from django.conf import settings


def enabled():
    return bool(settings.VAPID_PUBLIC_KEY and settings.VAPID_PRIVATE_KEY)


def _send_all(subs, payload):
    try:
        from pywebpush import WebPushException, webpush
    except Exception:
        return
    from .models import PushSubscription
    for sub in subs:
        try:
            webpush(
                subscription_info={"endpoint": sub["endpoint"], "keys": {"p256dh": sub["p256dh"], "auth": sub["auth"]}},
                data=json.dumps(payload),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": settings.VAPID_SUBJECT},
                ttl=3600,
            )
        except WebPushException as exc:
            status = getattr(getattr(exc, "response", None), "status_code", None)
            if status in (404, 410):  # abonelik gecersiz: sil
                PushSubscription.objects.filter(endpoint=sub["endpoint"]).delete()
        except Exception:
            pass


def notify_user(user, title, body, url="/", tag=None):
    """Kullanicinin tum cihazlarina arka planda bildirim gonderir; hata siteyi etkilemez."""
    if not enabled():
        return
    try:
        from .models import PushSubscription
        subs = list(PushSubscription.objects.filter(user=user).values("endpoint", "p256dh", "auth"))
        if not subs:
            return
        payload = {"title": title, "body": body, "url": url, "tag": tag or "bb"}
        threading.Thread(target=_send_all, args=(subs, payload), daemon=True).start()
    except Exception:
        pass


def notify_new_message(message):
    conv = message.conversation
    recipient = conv.other(message.sender)
    sender = message.sender.first_name or message.sender.username
    notify_user(recipient, sender, message.body[:120], url=f"/mesaj/{conv.pk}/", tag=f"conv-{conv.pk}")
